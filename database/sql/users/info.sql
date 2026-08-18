-- query: get_display_name
SELECT display_name
FROM users
WHERE user_id = $1;

-- query: get_username
SELECT username
FROM users
WHERE user_id = $1;

-- query: get_freeze_status
SELECT frozen
FROM users
WHERE user_id = $1;

-- query: get_freeze_invites_status
SELECT freeze_invites
FROM subscriptions
WHERE guild_id = $1
AND user_id = $2;

-- query: get_guild_users
SELECT u.*
FROM users AS u
JOIN subscriptions AS s
    ON u.user_id = s.user_id
WHERE s.guild_id = $1;

-- query: get_guild_user_ids
SELECT user_id
FROM subscriptions
WHERE guild_id = $1
ORDER BY user_id

-- query: get_user_from_discord_id
SELECT user_id
FROM users
WHERE discord_id = $1

-- query: get_discord_id_from_user
SELECT discord_id
FROM users
WHERE user_id = $1

-- query: get_all_users
SELECT *
FROM users
ORDER BY user_id

-- query: get_all_user_ids
SELECT user_id
FROM users
ORDER BY user_id

-- query: user_exists_in_ri
SELECT EXISTS (
    SELECT 1
    FROM users
    WHERE user_id = $1
)

-- query: prev_discord
SELECT *
FROM users
WHERE discord_id = $1

-- query: prev_roblox
SELECT *
FROM users
WHERE user_id = $1

-- query: user_exists_in_guild
SELECT EXISTS (
    SELECT 1
    FROM subscriptions
    WHERE guild_id = $1
    AND user_id = $2
)

-- query: get_deleted_users
SELECT user_id
FROM users
WHERE erased = 1