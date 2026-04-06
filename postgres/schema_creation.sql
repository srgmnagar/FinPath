-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    signup_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    device_type VARCHAR(20),
    country VARCHAR(20) DEFAULT 'IN',
    risk_profile VARCHAR(20),
    activated_at TIMESTAMP,
    first_deposit_at TIMESTAMP
);

-- Events table
CREATE TABLE IF NOT EXISTS events (
    event_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    event_type VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    properties JSONB,
    session_id TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_events_user_id ON events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_user_event ON events(user_id, event_type);