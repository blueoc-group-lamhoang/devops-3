CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

INSERT INTO todos (title, completed) VALUES
    ('Learn Docker', false),
    ('Deploy the app', true)
ON CONFLICT DO NOTHING;
