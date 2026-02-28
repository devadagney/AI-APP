import unittest
from datetime import date, timedelta

from service_logic import due_state, next_service_date


class ServiceLogicTest(unittest.TestCase):
    def test_next_service_date(self):
        due = next_service_date("2026-01-01", 180)
        self.assertEqual(due.isoformat(), "2026-06-30")

    def test_due_state_overdue(self):
        state, days = due_state(date.today() - timedelta(days=3))
        self.assertEqual(state, "Overdue")
        self.assertEqual(days, -3)

    def test_due_state_due_soon(self):
        state, days = due_state(date.today() + timedelta(days=2))
        self.assertEqual(state, "Due soon")
        self.assertEqual(days, 2)

    def test_due_state_scheduled(self):
        state, days = due_state(date.today() + timedelta(days=20))
        self.assertEqual(state, "Scheduled")
        self.assertEqual(days, 20)


if __name__ == "__main__":
    unittest.main()
