-- Add auto-renew preference and renewal metadata

-- 1) Add columns to users table if they don't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'auto_renew_enabled'
    ) THEN
        ALTER TABLE users ADD COLUMN auto_renew_enabled BOOLEAN DEFAULT FALSE;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'last_renewal_reminder_at'
    ) THEN
        ALTER TABLE users ADD COLUMN last_renewal_reminder_at TIMESTAMP WITH TIME ZONE;
    END IF;
END $$;

-- 2) Optional: track renewals
CREATE TABLE IF NOT EXISTS renewal_events (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan_name TEXT NOT NULL,
    event_type TEXT NOT NULL, -- reminder_3d, reminder_1d, reminder_expiring, expired
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_renewal_events_user_id ON renewal_events(user_id);


