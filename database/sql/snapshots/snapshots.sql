-- query: get_total_playtimes_unfiltered
SELECT
    t.user_id,
    t.total_playtime +
    COALESCE(
        EXTRACT(EPOCH FROM (NOW() - cp.start_time)),
        0
    ) AS total_playtime
FROM total_playtimes t
LEFT JOIN currently_playing cp
    ON t.user_id = cp.user_id
WHERE t.user_id = ANY($1)
ORDER BY t.total_playtime;

-- query: get_game_playtimes_unfiltered
SELECT
    gp.user_id,
    gp.place_id,
    gp.playtime +
    COALESCE(
        EXTRACT(EPOCH FROM (NOW() - cp.start_time)),
        0
    ) AS playtime
FROM game_playtimes gp
LEFT JOIN currently_playing cp
    ON gp.user_id = cp.user_id
    AND gp.place_id = cp.place_id
WHERE gp.user_id = ANY($1);

-- query: get_latest_snapshot_id
SELECT snapshot_id
FROM snapshot_metadata
WHERE guild_id = $1
ORDER BY snapshot_id DESC
LIMIT 1;

-- query: save_snapshot_metadata
INSERT INTO snapshot_metadata (guild_id)
VALUES ($1)
RETURNING snapshot_id;

-- query: save_total_playtime_snapshot
INSERT INTO total_playtime_snapshots (snapshot_id, user_id, total_playtime)
VALUES ($1, $2, $3)
ON CONFLICT (snapshot_id, user_id)
DO NOTHING;

-- query: save_game_playtime_snapshot
INSERT INTO game_playtime_snapshots (snapshot_id, user_id, place_id, playtime)
VALUES ($1, $2, $3, $4)
ON CONFLICT (snapshot_id, user_id, place_id)
DO NOTHING;

-- query: remove_last_snapshot
DELETE FROM snapshot_metadata
WHERE guild_id = $1
AND snapshot_id = $2;