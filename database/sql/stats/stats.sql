-- query: check_currently_playing
SELECT EXISTS (
    SELECT 1
    FROM currently_playing
    WHERE user_id = $1
);

-- query: check_if_game_played
SELECT EXISTS (
    SELECT 1
    FROM game_playtimes
    WHERE user_id = ANY($1)
    AND place_id = $2
);

-- query: get_current_place_id
SELECT place_id
FROM currently_playing
WHERE user_id = $1;

-- query: get_total_playtime
SELECT
    t.total_playtime +
    COALESCE(
        EXTRACT(EPOCH FROM (NOW() - cp.start_time)),
        0
    ) AS total_playtime
FROM total_playtimes t
LEFT JOIN currently_playing cp
    ON t.user_id = cp.user_id
WHERE t.user_id = $1;

-- query: get_total_game_playtime
SELECT playtime
FROM game_playtimes
WHERE place_id = $1;

-- query: get_game_playtime
SELECT playtime
FROM game_playtimes
WHERE user_id = $1
AND place_id = $2;

-- query: get_current_playtime
SELECT start_time
FROM currently_playing
WHERE user_id = $1;

-- query: get_current_playtime_placeid
SELECT start_time
FROM currently_playing
WHERE user_id = $1
AND place_id = $2;

-- query: get_current_playtimes
SELECT *
FROM currently_playing
WHERE user_id = ANY($1);

-- query: update_game_playtime
INSERT INTO game_playtimes (user_id, place_id, playtime)
VALUES ($1, $2, $3)
ON CONFLICT (user_id, place_id)
DO UPDATE SET
    playtime = game_playtimes.playtime + EXCLUDED.playtime;

-- query: get_static_total_userid
SELECT playtime
FROM game_playtimes
WHERE user_id = $1

-- query: update_total_playtime
INSERT INTO total_playtimes (user_id, total_playtime)
VALUES ($1, $2)
ON CONFLICT (user_id)
DO UPDATE SET
    total_playtime = EXCLUDED.total_playtime;

-- query: set_currently_playing
INSERT INTO currently_playing (user_id, place_id)
VALUES ($1, $2);

-- query: remove_currently_playing
DELETE FROM currently_playing
WHERE user_id = $1;