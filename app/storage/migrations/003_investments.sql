-- Schema for investments

CREATE TABLE IF NOT EXISTS investments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    provider TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('MF', 'STOCK', 'FD', 'GOLD')),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS investment_contributions (
    id TEXT PRIMARY KEY,
    investment_id TEXT NOT NULL,
    date TEXT NOT NULL,
    amount TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (investment_id) REFERENCES investments(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS investment_value_snapshots (
    id TEXT PRIMARY KEY,
    investment_id TEXT NOT NULL,
    date TEXT NOT NULL,
    current_value TEXT NOT NULL,
    FOREIGN KEY (investment_id) REFERENCES investments(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_investment_contributions_investment ON investment_contributions(investment_id);
CREATE INDEX IF NOT EXISTS idx_investment_contributions_date ON investment_contributions(date);
CREATE INDEX IF NOT EXISTS idx_investment_snapshots_investment ON investment_value_snapshots(investment_id);
CREATE INDEX IF NOT EXISTS idx_investment_snapshots_date ON investment_value_snapshots(date);

-- Made with Bob
