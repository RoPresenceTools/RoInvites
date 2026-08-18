WITH snapshot_users AS (
    SELECT DISTINCT user_id
    FROM game_playtime_snapshots
    WHERE snapshot_id = $1
),

game_sls AS (
    SELECT
        p.user_id,
        CASE
            WHEN COALESCE(g.playtime, 0) - COALESCE(s.playtime, 0) > 0 THEN COALESCE(g.playtime, 0) - COALESCE(s.playtime, 0)
            ELSE 0
        END AS playtime
    FROM snapshot_users p

    LEFT JOIN game_playtime_snapshots s
        ON s.snapshot_id = $1
        AND s.user_id = p.user_id
        AND s.place_id = $2

    LEFT JOIN game_playtimes g
        ON g.user_id = p.user_id
        AND g.place_id = $2
),

live_playtime AS (
    SELECT
        cp.user_id,
        SUM(EXTRACT(EPOCH FROM (NOW() - cp.start_time))) AS playtime
    FROM currently_playing cp
    JOIN snapshot_users u
        ON u.user_id = cp.user_id
    WHERE cp.place_id = $2
    GROUP BY cp.user_id
)

SELECT SUM(playtime)
FROM (
    SELECT
        g.user_id,
        g.playtime + COALESCE(l.playtime, 0) AS playtime,
        RANK() OVER (
            ORDER BY g.playtime + COALESCE(l.playtime, 0) DESC
        ) AS rank
    FROM game_sls g
    LEFT JOIN live_playtime l
        ON l.user_id = g.user_id
    WHERE g.playtime + COALESCE(l.playtime, 0) > 0
    ORDER BY playtime DESC
)