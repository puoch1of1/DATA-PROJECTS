DROP TABLE IF EXISTS email_subscribers;

CREATE TABLE email_subscribers (
    subscriber_id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    signup_source VARCHAR(100),
    signup_date DATE DEFAULT CURRENT_DATE NOT NULL,
    country VARCHAR(100)
);
