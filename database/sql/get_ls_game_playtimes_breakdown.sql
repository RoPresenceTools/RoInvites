SELECT
    user_id,
    place_id,
    playtime,
    RANK() OVER (ORDER BY playtime DESC) AS rank
FROM (
    SELECT
        s.user_id,
        s.place_id,
        COALESCE(g.playtime, 0)
        + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0)
        - s.playtime AS playtime
    FROM game_playtime_snapshots s
    LEFT JOIN game_playtimes g
        ON g.user_id = s.user_id
        AND g.place_id = s.place_id
    LEFT JOIN currently_playing cp
        ON cp.user_id = s.user_id
        AND cp.place_id = s.place_id
    WHERE s.snapshot_id = $1
    AND s.place_id = $2
) games_ranked
WHERE playtime > 0
LIMIT 10
OFFSET $3