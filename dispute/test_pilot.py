"""Build a synthetic log and check the pilot invariants."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import unittest

class DisputePilot(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.addCleanup(self.db.close)
        self.db.executescript(Path(__file__).with_name("schema.sql").read_text())
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        for case, outcome, decision in [(1, "accepted", 48), (2, "rejected", 80)]:
            def at(hours):
                return (start + timedelta(hours=hours)).isoformat()
            self.db.execute("INSERT INTO dispute VALUES (?,?,?,?,?,?,?,?)",
                            (case, f"DEMO-{case}", f"TX-{case}", "duplicate",
                             at(0), at(72), "demo-1", outcome))
            events = [("received", 0, "intake"), ("evidence_ready", 24, "evidence"),
                      ("slot_ready", 12, "scheduler"), ("decided", decision, "reviewer"),
                      ("notified", decision + 1, "notification"),
                      ("closed", decision + 2, "reviewer")]
            if decision > 72:
                events.append(("escalated", 72, "supervisor"))
            self.db.executemany("INSERT INTO dispute_event VALUES (?,?,?,?)",
                                [(case, name, at(hour), role) for name, hour, role in events])

    def test_case_sequences(self):
        for case, due in self.db.execute("SELECT id, decision_due_at FROM dispute"):
            events = dict(self.db.execute(
                "SELECT activity, occurred_at FROM dispute_event WHERE dispute_id=?", (case,)))
            self.assertLessEqual(max(events["evidence_ready"], events["slot_ready"]), events["decided"])
            self.assertLessEqual(events["decided"], events["notified"])
            self.assertLessEqual(events["notified"], events["closed"])
            self.assertEqual(events["decided"] > due, "escalated" in events)

    def test_duplicate_submission(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO dispute SELECT id+10, submission_key, transaction_ref,"
                            " category, received_at, decision_due_at, policy_version, outcome"
                            " FROM dispute WHERE id=1")

    def test_duplicate_notification(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute("INSERT INTO dispute_event SELECT * FROM dispute_event"
                            " WHERE dispute_id=1 AND activity='notified'")

if __name__ == "__main__":
    unittest.main()
