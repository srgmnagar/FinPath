-- Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    signup_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    device_type VARCHAR(20),
    country VARCHAR(20) DEFAULT 'IN',
    risk_profile VARCHAR(20),
    activated_at TIMESTAMP,
    first_deposit_at TIMESTAMP
);


-- events table
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    event_type VARCHAR(100),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    properties JSONB
);