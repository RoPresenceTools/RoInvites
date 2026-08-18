-- query: get_entries_agg_game_playtimes
SELECT COUNT(*)
FROM (
    SELECT
        g.place_id,
        SUM(
            COALESCE(g.playtime, 0)
            + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0)
        ) AS playtime
    FROM game_playtimes g
    LEFT JOIN currently_playing cp
        ON cp.user_id = g.user_id
        AND cp.place_id = g.place_id
    WHERE g.user_id = ANY($1)
    AND playtime > 0
    GROUP BY g.place_id
) games_ranked;

-- query: get_total_agg_game_playtimes
SELECT SUM(playtime)
FROM (
    SELECT
        g.place_id,
        SUM(
            COALESCE(g.playtime, 0)
            + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0)
        ) AS playtime
    FROM game_playtimes g
    LEFT JOIN currently_playing cp
        ON cp.user_id = g.user_id
        AND cp.place_id = g.place_id
    WHERE g.user_id = ANY($1)
    AND playtime > 0
    GROUP BY g.place_id
) games_ranked;

-- query: get_agg_game_playtimes
SELECT
    place_id,
    playtime,
    RANK() OVER (ORDER BY playtime DESC) AS rank
FROM (
    SELECT
        g.place_id,
        SUM(
            COALESCE(g.playtime, 0)
            + COALESCE(EXTRACT(EPOCH FROM (NOW() - cp.start_time)), 0)
        ) AS playtime
    FROM game_playtimes g
    LEFT JOIN currently_playing cp
        ON cp.user_id = g.user_id
        AND cp.place_id = g.place_id
    WHERE g.user_id = ANY($1)
    AND playtime > 0
    GROUP BY g.place_id
) games_ranked
LIMIT 10
OFFSET $2;