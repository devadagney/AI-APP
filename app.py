from __future__ import annotations

import os
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any

from flask import Flask, flash, redirect, render_template, request, url_for

from service_logic import due_state, next_service_date

DB_PATH = Path(__file__).with_name("service.db")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                purifier_model TEXT,
                last_service_date TEXT NOT NULL,
                service_interval_days INTEGER NOT NULL DEFAULT 180,
                notes TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reminder_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                sent_at TEXT NOT NULL,
                channel TEXT NOT NULL,
                message TEXT NOT NULL,
                FOREIGN KEY(customer_id) REFERENCES customers(id)
            )
            """
        )


def customer_view(row: sqlite3.Row) -> dict[str, Any]:
    next_due = next_service_date(row["last_service_date"], row["service_interval_days"])
    state, delta_days = due_state(next_due)
    return {
        **dict(row),
        "next_service_date": next_due.isoformat(),
        "status": state,
        "days_until_due": delta_days,
    }


@app.route("/")
def index():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM customers ORDER BY id DESC").fetchall()
        reminders = conn.execute(
            """
            SELECT r.sent_at, r.channel, r.message, c.name AS customer_name
            FROM reminder_log r
            JOIN customers c ON c.id = r.customer_id
            ORDER BY r.id DESC
            LIMIT 20
            """
        ).fetchall()

    customers = [customer_view(r) for r in rows]
    due_customers = [c for c in customers if c["status"] in {"Overdue", "Due soon"}]

    return render_template(
        "index.html",
        customers=customers,
        due_customers=due_customers,
        reminder_log=reminders,
        today=date.today().isoformat(),
    )


@app.post("/customers")
def add_customer():
    form = request.form
    name = form.get("name", "").strip()
    if not name:
        flash("Customer name is required.", "error")
        return redirect(url_for("index"))

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO customers
            (name, phone, email, purifier_model, last_service_date, service_interval_days, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                form.get("phone", "").strip(),
                form.get("email", "").strip(),
                form.get("purifier_model", "").strip(),
                form.get("last_service_date", date.today().isoformat()),
                int(form.get("service_interval_days") or 180),
                form.get("notes", "").strip(),
                datetime.now().isoformat(timespec="seconds"),
            ),
        )

    flash("Customer added.", "success")
    return redirect(url_for("index"))


@app.post("/customers/<int:customer_id>/mark-serviced")
def mark_serviced(customer_id: int):
    with get_db() as conn:
        conn.execute(
            "UPDATE customers SET last_service_date = ? WHERE id = ?",
            (date.today().isoformat(), customer_id),
        )
    flash("Service date updated to today.", "success")
    return redirect(url_for("index"))


@app.post("/customers/<int:customer_id>/send-reminder")
def send_reminder(customer_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
        if not row:
            flash("Customer not found.", "error")
            return redirect(url_for("index"))

        customer = customer_view(row)
        message = (
            f"Hi {customer['name']}, this is a reminder that your water purifier service is "
            f"due on {customer['next_service_date']}. Please schedule your service visit."
        )
        channel = "email" if customer.get("email") else "phone"

        conn.execute(
            "INSERT INTO reminder_log (customer_id, sent_at, channel, message) VALUES (?, ?, ?, ?)",
            (customer_id, datetime.now().isoformat(timespec="seconds"), channel, message),
        )

    flash("Reminder queued and logged.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
