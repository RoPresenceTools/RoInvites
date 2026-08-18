-- query: get_entries_total_playtimes
SELECT COUNT(*)
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

-- query: get_total_total_playtimes
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

-- query: get_total_playtimes
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
LIMIT 10
OFFSET $2