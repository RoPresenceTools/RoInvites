-- query: check_blacklist
SELECT EXISTS (
    SELECT 1
    FROM blacklist
    WHERE guild_id = $1
    AND place_id = $2
);

-- query: add_blacklist
INSERT INTO blacklist (guild_id, place_id, game_name)
VALUES ($1, $2, $3);

-- query: remove_blacklist
DELETE FROM blacklist
WHERE guild_id = $1
AND place_id = $2;

-- query: get_blacklisted_games
SELECT *
FROM blacklist
WHERE guild_id = $1
AND game_name ILIKE '%' || $2 || '%'
LIMIT 25;