# Water Purifier Service Tracker

This app helps you maintain customer service due dates for water purifiers, track when a customer needs service again, and log reminders sent to clients.

## Features
- Add customers with contact details, purifier model, last service date, and service interval.
- Automatically calculate the next service date.
- Highlight customers as **Overdue**, **Due soon**, or **Scheduled**.
- Mark service as completed (updates last service date to today).
- Send/log reminder messages for due customers.
- Keep a recent reminder history.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open: http://localhost:5000

## Run tests
```bash
python -m unittest discover -s tests
```
