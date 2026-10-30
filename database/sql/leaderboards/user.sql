-- query: get_entries_game_playtimes
SELECT COUNT(*)
FROM game_playtimes
WHERE user_id = $1;

-- query: get_total_game_playtimes
SELECT SUM(playtime)
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
    WHERE g.user_id = $1
) games_ranked;

-- query: get_game_playtimes
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
    WHERE g.user_id = $1
) games_ranked
LIMIT 10
OFFSET $2;

-- query: get_entries_ls_game_playtimes
WITH game_pairs AS (
    SELECT user_id, place_id
    FROM game_playtime_snapshots
    WHERE snapshot_id = $1
    AND user_id = $2

    UNION

    SELECT g.user_id, g.place_id
    FROM game_playtimes g
    WHERE g.user_id = $2
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

    WHERE p.user_id = $2
    GROUP BY p.place_id
),

live_playtime AS (
    SELECT
        cp.place_id,
        SUM(EXTRACT(EPOCH FROM (NOW() - cp.start_time))) AS playtime
    FROM currently_playing cp
    WHERE cp.user_id = $2
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

-- query: get_total_ls_game_playtimes
WITH game_pairs AS (
    SELECT user_id, place_id
    FROM game_playtime_snapshots
    WHERE snapshot_id = $1
    AND user_id = $2

    UNION

    SELECT g.user_id, g.place_id
    FROM game_playtimes g
    WHERE g.user_id = $2
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

    WHERE p.user_id = $2
    GROUP BY p.place_id
),

live_playtime AS (
    SELECT
        cp.place_id,
        SUM(EXTRACT(EPOCH FROM (NOW() - cp.start_time))) AS playtime
    FROM currently_playing cp
    WHERE cp.user_id = $2
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

-- query: get_ls_game_playtimes
WITH game_pairs AS (
    SELECT user_id, place_id
    FROM game_playtime_snapshots
    WHERE snapshot_id = $1
    AND user_id = $2

    UNION

    SELECT g.user_id, g.place_id
    FROM game_playtimes g
    WHERE g.user_id = $2
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

    WHERE p.user_id = $2
    GROUP BY p.place_id
),

live_playtime AS (
    SELECT
        cp.place_id,
        SUM(EXTRACT(EPOCH FROM (NOW() - cp.start_time))) AS playtime
    FROM currently_playing cp
    WHERE cp.user_id = $2
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
OFFSET $3;