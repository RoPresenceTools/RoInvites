-- 001_presence_updates.sql
ALTER TABLE presences
ADD IF NOT EXISTS last_location TEXT,
ADD IF NOT EXISTS root_place_id BIGINT DEFAULT 0;

ALTER TABLE old_presences
ADD IF NOT EXISTS last_location TEXT,
ADD IF NOT EXISTS root_place_id BIGINT DEFAULT 0;

-- 002_db_metadata.sql
CREATE TABLE IF NOT EXISTS metadata (
    id INT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    current_version TEXT DEFAULT '0.0.0'
);

-- 003_privacy_controls.sql
ALTER TABLE users
ADD IF NOT EXISTS frozen INT DEFAULT 0;

ALTER TABLE subscriptions
ADD IF NOT EXISTS freeze_invites INT DEFAULT 0;