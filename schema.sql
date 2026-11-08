-- PostgreSQL schema for the Telegram automation application
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS app_users (
    user_id TEXT PRIMARY KEY,
    phone TEXT,
    authenticated BOOLEAN NOT NULL DEFAULT FALSE,
    connected BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_settings (
    user_id TEXT PRIMARY KEY REFERENCES app_users(user_id) ON DELETE CASCADE,
    settings JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sent_batches (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES app_users(user_id) ON DELETE CASCADE,
    batch_id TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    sent_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, batch_id)
);

CREATE TABLE IF NOT EXISTS schedule_events (
    id BIGSERIAL PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES app_users(user_id) ON DELETE CASCADE,
    phase TEXT NOT NULL CHECK (phase IN ('running', 'paused', 'resumed', 'stopped', 'expired')),
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS push_subscriptions (
    user_id TEXT NOT NULL REFERENCES app_users(user_id) ON DELETE CASCADE,
    endpoint TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, endpoint)
);

CREATE INDEX IF NOT EXISTS idx_sent_batches_user_sent_at ON sent_batches(user_id, sent_at DESC);
CREATE INDEX IF NOT EXISTS idx_schedule_events_user_recorded_at ON schedule_events(user_id, recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_schedule_events_phase ON schedule_events(phase);

INSERT INTO schema_migrations(version)
VALUES (1)
ON CONFLICT (version) DO NOTHING;
