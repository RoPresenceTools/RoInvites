-- query: get_custom_title
SELECT *
FROM custom_titles
WHERE guild_id = $1
AND universe_id = $2;

-- query: get_custom_title_rpid
SELECT *
FROM custom_titles
WHERE guild_id = $1
AND root_place_id = $2;

-- query: check_custom_title
SELECT EXISTS (
    SELECT 1
    FROM custom_titles
    WHERE guild_id = $1
    AND universe_id = $2
);

-- query: add_custom_title
INSERT INTO custom_titles (guild_id, universe_id, title, color, game_name, root_place_id)
VALUES ($1, $2, $3, $4, $5, $6)
ON CONFLICT (guild_id, universe_id)
DO NOTHING
RETURNING guild_id;

-- query: remove_custom_title
DELETE FROM custom_titles
WHERE guild_id = $1
AND universe_id = $2
RETURNING universe_id;

-- query: get_cgt_games
SELECT *
FROM custom_titles
WHERE guild_id = $1
AND game_name ILIKE '%' || $2 || '%'
LIMIT 25;