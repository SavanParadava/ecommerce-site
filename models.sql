CREATE TABLE IF NOT EXISTS admin_users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    owner TEXT NOT NULL REFERENCES admin_users(username),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- psql -U youruser -d yourdb -f models.sql