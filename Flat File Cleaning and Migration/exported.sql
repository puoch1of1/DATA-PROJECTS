DROP TABLE IF EXISTS email_subscribers;

CREATE TABLE email_subscribers (
    subscriber_id SERIAL PRIMARY KEY,
    source_id INTEGER,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    signup_source VARCHAR(100) NOT NULL DEFAULT 'Unknown',
    signup_date DATE NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'Unknown',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_email_subscribers_email UNIQUE (email),
    CONSTRAINT chk_email_subscribers_full_name CHECK (LENGTH(BTRIM(full_name)) > 0),
    CONSTRAINT chk_email_subscribers_country CHECK (LENGTH(BTRIM(country)) > 0),
    CONSTRAINT chk_email_subscribers_email CHECK (POSITION('@' IN email) > 1)
);

CREATE INDEX idx_email_subscribers_signup_date
    ON email_subscribers (signup_date);
