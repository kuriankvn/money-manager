-- Initial schema for accounts and transactions

CREATE TABLE IF NOT EXISTS accounts (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('BANK', 'CARD')),
    institution TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    date TEXT NOT NULL,
    amount TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);

-- Made with Bob
