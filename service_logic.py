from __future__ import annotations

from datetime import date, datetime, timedelta


def parse_iso_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def next_service_date(last_service_date: str, interval_days: int) -> date:
    return parse_iso_date(last_service_date) + timedelta(days=interval_days)


def due_state(next_due: date) -> tuple[str, int]:
    delta_days = (next_due - date.today()).days
    if delta_days < 0:
        return "Overdue", delta_days
    if delta_days <= 7:
        return "Due soon", delta_days
    return "Scheduled", delta_days
