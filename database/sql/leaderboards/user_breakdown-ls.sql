-- query: get_entries_ls_total_playtimes
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
WHERE total_playtime > 0;

-- query: get_total_ls_total_playtimes
SELECT SUM(total_playtime)
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
WHERE total_playtime > 0;

-- query: get_ls_total_playtimes
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
WHERE total_playtime > 0
LIMIT 10
OFFSET $3;