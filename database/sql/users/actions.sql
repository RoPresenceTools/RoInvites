-- query: add_user
INSERT INTO users (user_id, discord_id, username, display_name)
VALUES ($1, $2, $3, $4)
ON CONFLICT (user_id)
DO UPDATE SET
    username = EXCLUDED.username,
    display_name = EXCLUDED.display_name

-- query: remove_user
UPDATE users
SET erased = 1
WHERE user_id = $1

-- query: link_user
INSERT INTO subscriptions (guild_id, user_id)
VALUES ($1, $2)
ON CONFLICT (guild_id, user_id)
DO NOTHING

-- query: unlink_user
DELETE FROM subscriptions
WHERE guild_id = $1
AND user_id = $2

-- query: modify_server_invites
UPDATE subscriptions
SET freeze_invites = $3
WHERE guild_id = $1
AND user_id = $2

-- query: modify_freeze_user
UPDATE users
SET frozen = $2
WHERE user_id = $1

-- query: remove_deleted_subscriptions
DELETE FROM subscriptions
WHERE user_id = ANY($1);

-- query: remove_deleted_users
DELETE FROM users
WHERE user_id = ANY($1);

-- query: remove_deleted_currently_playing
DELETE FROM currently_playing
WHERE user_id = ANY($1);

-- query: remove_deleted_game_playtimes
DELETE FROM game_playtimes
WHERE user_id = ANY($1);

-- query: remove_deleted_total_playtimes
DELETE FROM total_playtimes
WHERE user_id = ANY($1);

-- query: remove_deleted_presences
DELETE FROM presences
WHERE user_id = ANY($1);

-- query: remove_deleted_old_presences
DELETE FROM old_presences
WHERE user_id = ANY($1);

-- query: update_user_info
INSERT INTO users (user_id, discord_id, username, display_name)
VALUES ($1, $2, $3, $4)
ON CONFLICT (user_id)
DO UPDATE SET
    username = EXCLUDED.username,
    display_name = EXCLUDED.display_name