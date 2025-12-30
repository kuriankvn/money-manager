-- Schema for subscriptions and subscription instances

CREATE TABLE IF NOT EXISTS subscriptions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('BILL', 'INSURANCE', 'OTHER')),
    frequency TEXT NOT NULL CHECK (frequency IN ('MONTHLY', 'YEARLY')),
    due_day INTEGER NOT NULL CHECK (due_day >= 1 AND due_day <= 31),
    expected_amount TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS subscription_instances (
    id TEXT PRIMARY KEY,
    subscription_id TEXT NOT NULL,
    period TEXT NOT NULL,
    due_date TEXT NOT NULL,
    amount TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('DUE', 'PAID')),
    paid_date TEXT,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_subscription_instances_subscription ON subscription_instances(subscription_id);
CREATE INDEX IF NOT EXISTS idx_subscription_instances_period ON subscription_instances(period);
CREATE INDEX IF NOT EXISTS idx_subscription_instances_status ON subscription_instances(status);

-- Made with Bob
