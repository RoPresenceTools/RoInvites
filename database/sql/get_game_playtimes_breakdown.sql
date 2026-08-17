SELECT
    user_id,
    place_id,
    playtime,
    RANK() OVER (ORDER BY playtime DESC) AS rank
FROM (
    SELECT
        g.user_id,
        g.place_id,
        COALESCE(g.playtime, 0)
        + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0) AS playtime
    FROM game_playtimes g
    LEFT JOIN currently_playing cp
        ON cp.user_id = g.user_id
        AND cp.place_id = g.place_id
    WHERE g.user_id = ANY($1)
    AND g.place_id = $2
) games_ranked
LIMIT 10
OFFSET $3