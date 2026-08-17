SELECT COUNT(*)
FROM (
    SELECT
        s.user_id,
        t.total_playtime
        - COALESCE(s.total_playtime, 0)
        + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0) AS total_playtime
    FROM total_playtime_snapshots s
    LEFT JOIN total_playtimes t
        ON t.user_id = s.user_id
    LEFT JOIN currently_playing cp
        ON cp.user_id = s.user_id
    WHERE s.snapshot_id = $1
    AND s.user_id = ANY($2)
) playtimes
WHERE total_playtime > 0