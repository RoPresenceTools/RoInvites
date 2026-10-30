-- query: get_transfer
SELECT *
FROM transfers
WHERE user_id = $1;

-- query: check_transfer
SELECT EXISTS (
    SELECT 1
    FROM transfers
    WHERE user_id = $1
);

-- query: add_transfer
INSERT INTO transfers (user_id, old_game_instance_id, old_place_id)
VALUES ($1, $2, $3)
ON CONFLICT (user_id)
DO UPDATE SET
    old_game_instance_id = EXCLUDED.old_game_instance_id,
    old_place_id = EXCLUDED.old_place_id;

-- query: remove_transfer
DELETE FROM transfers
WHERE user_id = $1;