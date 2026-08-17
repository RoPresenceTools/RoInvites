SELECT SUM(total_playtime)
FROM (
    SELECT
        t.user_id,
        COALESCE(t.total_playtime, 0)
        + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0) AS total_playtime
    FROM total_playtimes t
    LEFT JOIN currently_playing cp
        ON cp.user_id = t.user_id
    WHERE t.user_id = ANY($1)
) playtimes