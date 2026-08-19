-- query: get_announcement_channel
SELECT announcement_channel
FROM guild_settings
WHERE guild_id = $1;

-- query: get_invite_channel
SELECT invite_channel
FROM guild_settings
WHERE guild_id = $1;

-- query: set_announcement_channel
UPDATE guild_settings
SET announcement_channel = $2
WHERE guild_id = $1;

-- query: set_invite_channel
UPDATE guild_settings
SET invite_channel = $2
WHERE guild_id = $1;