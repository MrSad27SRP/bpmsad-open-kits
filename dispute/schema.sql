PRAGMA foreign_keys = ON;
CREATE TABLE dispute (
    id INTEGER PRIMARY KEY,
    submission_key TEXT NOT NULL UNIQUE CHECK (length(trim(submission_key)) > 0),
    transaction_ref TEXT NOT NULL CHECK (length(trim(transaction_ref)) > 0),
    category TEXT NOT NULL CHECK (category IN ('duplicate', 'missing', 'incorrect')),
    received_at TEXT NOT NULL,
    decision_due_at TEXT NOT NULL CHECK (decision_due_at >= received_at),
    policy_version TEXT NOT NULL,
    outcome TEXT CHECK (outcome IN ('accepted', 'rejected'))
);
CREATE TABLE dispute_event (
    dispute_id INTEGER NOT NULL REFERENCES dispute(id),
    activity TEXT NOT NULL CHECK (activity IN (
        'received', 'evidence_ready', 'slot_ready', 'escalated', 'decided', 'notified', 'closed'
    )),
    occurred_at TEXT NOT NULL,
    actor_role TEXT NOT NULL,
    PRIMARY KEY (dispute_id, activity)
);
