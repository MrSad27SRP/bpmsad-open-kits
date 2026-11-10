"""Check one closed pilot case against a normalized evidence export."""
import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path


def utc(value):
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if stamp.utcoffset() != timedelta(0):
        raise ValueError("Timestamp must include a UTC offset of zero")
    return stamp


def verify(case):
    if not case["case_id"] or case["outcome"] not in ("accepted", "rejected"):
        raise ValueError("Expected a case ID and a persisted decision outcome")
    due = utc(case["decision_due_at"])
    times = {}
    for event in case["events"]:
        activity = event["activity"]
        if activity in times:
            raise ValueError(f"Duplicate activity: {activity}")
        times[activity] = utc(event["occurred_at"])
    received, evidence, slot, decided, notified, closed = (
        times[name] for name in
        ("received", "evidence_ready", "slot_ready", "decided", "notified", "closed")
    )
    if not (received <= min(evidence, slot) <= max(evidence, slot)
            <= decided <= notified <= closed and received <= due):
        raise ValueError("Invalid milestone order or deadline")
    escalation = times.get("escalated")
    if decided > due:
        if escalation is None or not due <= escalation < decided:
            raise ValueError("Expected one escalation between deadline and decision")
    elif escalation is not None:
        raise ValueError("An on-time decision must not be escalated")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path)
    args = parser.parse_args()
    try:
        verify(json.loads(args.export.read_text(encoding="utf-8-sig")))
    except (OSError, AttributeError, KeyError, TypeError, ValueError) as error:
        parser.exit(1, f"FAIL: {error}\n")
    print("PASS: decision, milestone order and escalation count")


if __name__ == "__main__":
    main()
