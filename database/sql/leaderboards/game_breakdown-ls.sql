-- query: get_entries_agg_ls_game_playtimes
WITH snapshot_users AS (
    SELECT DISTINCT user_id
    FROM game_playtime_snapshots
    WHERE snapshot_id = $1
),

game_pairs AS (
    SELECT user_id, place_id
    FROM game_playtime_snapshots
    WHERE snapshot_id = $1

    UNION

    SELECT g.user_id, g.place_id
    FROM game_playtimes g
    JOIN snapshot_users u
        ON u.user_id = g.user_id
),

game_sls AS (
    SELECT
        p.place_id,
        SUM(
            CASE
                WHEN COALESCE(g.playtime, 0) - COALESCE(s.playtime, 0) > 0 THEN COALESCE(g.playtime, 0) - COALESCE(s.playtime, 0)
                ELSE 0
            END
        ) AS playtime
    FROM game_pairs p

    LEFT JOIN game_playtime_snapshots s
        ON s.snapshot_id = $1
        AND s.user_id = p.user_id
        AND s.place_id = p.place_id

    LEFT JOIN game_playtimes g
        ON g.user_id = p.user_id
        AND g.place_id = p.place_id

    GROUP BY p.place_id
),

live_playtime AS (
    SELECT
        cp.place_id,
        SUM(EXTRACT(EPOCH FROM (NOW() - cp.start_time))) AS playtime
    FROM currently_playing cp
    JOIN snapshot_users u
        ON u.user_id = cp.user_id
    GROUP BY cp.place_id
)

SELECT COUNT(*)
FROM (
    SELECT
        g.place_id,
        g.playtime + COALESCE(l.playtime, 0) AS playtime,
        RANK() OVER (
            ORDER BY g.playtime + COALESCE(l.playtime, 0) DESC
        ) AS rank
    FROM game_sls g
    LEFT JOIN live_playtime l
        ON l.place_id = g.place_id
    WHERE g.playtime + COALESCE(l.playtime, 0) > 0
    ORDER BY playtime DESC
);

-- query: get_total_agg_ls_game_playtimes
WITH snapshot_users AS (
    SELECT DISTINCT user_id
    FROM game_playtime_snapshots
    WHERE snapshot_id = $1
),

game_pairs AS (
    SELECT user_id, place_id
    FROM game_playtime_snapshots
    WHERE snapshot_id = $1

    UNION

    SELECT g.user_id, g.place_id
    FROM game_playtimes g
    JOIN snapshot_users u
        ON u.user_id = g.user_id
),

game_sls AS (
    SELECT
        p.place_id,
        SUM(
            CASE
                WHEN COALESCE(g.playtime, 0) - COALESCE(s.playtime, 0) > 0 THEN COALESCE(g.playtime, 0) - COALESCE(s.playtime, 0)
                ELSE 0
            END
        ) AS playtime
    FROM game_pairs p

    LEFT JOIN game_playtime_snapshots s
        ON s.snapshot_id = $1
        AND s.user_id = p.user_id
        AND s.place_id = p.place_id

    LEFT JOIN game_playtimes g
        ON g.user_id = p.user_id
        AND g.place_id = p.place_id

    GROUP BY p.place_id
),

live_playtime AS (
    SELECT
        cp.place_id,
        SUM(EXTRACT(EPOCH FROM (NOW() - cp.start_time))) AS playtime
    FROM currently_playing cp
    JOIN snapshot_users u
        ON u.user_id = cp.user_id
    GROUP BY cp.place_id
)

SELECT SUM(playtime)
FROM (
    SELECT
        g.place_id,
        g.playtime + COALESCE(l.playtime, 0) AS playtime,
        RANK() OVER (
            ORDER BY g.playtime + COALESCE(l.playtime, 0) DESC
        ) AS rank
    FROM game_sls g
    LEFT JOIN live_playtime l
        ON l.place_id = g.place_id
    WHERE g.playtime + COALESCE(l.playtime, 0) > 0
    ORDER BY playtime DESC
);

-- query: get_agg_ls_game_playtimes
WITH snapshot_users AS (
    SELECT DISTINCT user_id
    FROM game_playtime_snapshots
    WHERE snapshot_id = $1
),

game_pairs AS (
    SELECT user_id, place_id
    FROM game_playtime_snapshots
    WHERE snapshot_id = $1

    UNION

    SELECT g.user_id, g.place_id
    FROM game_playtimes g
    JOIN snapshot_users u
        ON u.user_id = g.user_id
),

game_sls AS (
    SELECT
        p.place_id,
        SUM(
            CASE
                WHEN COALESCE(g.playtime, 0) - COALESCE(s.playtime, 0) > 0 THEN COALESCE(g.playtime, 0) - COALESCE(s.playtime, 0)
                ELSE 0
            END
        ) AS playtime
    FROM game_pairs p

    LEFT JOIN game_playtime_snapshots s
        ON s.snapshot_id = $1
        AND s.user_id = p.user_id
        AND s.place_id = p.place_id

    LEFT JOIN game_playtimes g
        ON g.user_id = p.user_id
        AND g.place_id = p.place_id

    GROUP BY p.place_id
),

live_playtime AS (
    SELECT
        cp.place_id,
        SUM(EXTRACT(EPOCH FROM (NOW() - cp.start_time))) AS playtime
    FROM currently_playing cp
    JOIN snapshot_users u
        ON u.user_id = cp.user_id
    GROUP BY cp.place_id
)

SELECT
    g.place_id,
    g.playtime + COALESCE(l.playtime, 0) AS playtime,
    RANK() OVER (
        ORDER BY g.playtime + COALESCE(l.playtime, 0) DESC
    ) AS rank
FROM game_sls g
LEFT JOIN live_playtime l
    ON l.place_id = g.place_id
WHERE g.playtime + COALESCE(l.playtime, 0) > 0
ORDER BY playtime DESC
LIMIT 10
OFFSET $2;