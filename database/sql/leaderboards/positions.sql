-- query: get_leaderboard_position
SELECT rank
FROM (
    SELECT
        user_id,
        total_playtime,
        RANK() OVER (ORDER BY total_playtime DESC) AS rank
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
) ranked
WHERE user_id = $2;

-- query: get_ls_leaderboard_position
SELECT rank
FROM (
    SELECT
        user_id,
        total_playtime,
        RANK() OVER (ORDER BY total_playtime DESC) AS rank
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
)
WHERE user_id = $3;