-- query: get_all_presences
SELECT *
FROM presences;

-- query: save_current_presences
INSERT INTO presences (user_id, last_location, place_id, root_place_id, game_instance_id, user_status)
VALUES ($1, $2, $3, $4, $5, $6)
ON CONFLICT (user_id)
DO UPDATE SET
    last_location = EXCLUDED.last_location,
    place_id = EXCLUDED.place_id,
    root_place_id = EXCLUDED.root_place_id,
    game_instance_id = EXCLUDED.game_instance_id,
    user_status = EXCLUDED.user_status;

-- query: save_old_presences
INSERT INTO old_presences (user_id, last_location, place_id, root_place_id, game_instance_id, user_status)
VALUES ($1, $2, $3, $4, $5, $6)
ON CONFLICT (user_id)
DO UPDATE SET
    last_location = EXCLUDED.last_location,
    place_id = EXCLUDED.place_id,
    root_place_id = EXCLUDED.root_place_id,
    game_instance_id = EXCLUDED.game_instance_id,
    user_status = EXCLUDED.user_status;

-- query: erase_presence
INSERT INTO presences (user_id, last_location, place_id, root_place_id, game_instance_id, user_status)
VALUES ($1, $2, $3, $4, $5, $6)
ON CONFLICT (user_id)
DO UPDATE SET
    last_location = EXCLUDED.last_location,
    place_id = EXCLUDED.place_id,
    root_place_id = EXCLUDED.root_place_id,
    game_instance_id = EXCLUDED.game_instance_id,
    user_status = EXCLUDED.user_status;

-- query: get_presence
SELECT *
FROM presences
WHERE user_id = $1;

-- query: get_current_guild_presences
SELECT p.*
FROM presences AS p
JOIN subscriptions AS s
    ON p.user_id = s.user_id
WHERE s.guild_id = $1;

-- query: get_old_guild_presences
SELECT p.*
FROM old_presences AS p
JOIN subscriptions AS s
    ON p.user_id = s.user_id
WHERE s.guild_id = $1;

-- query: get_all_users
SELECT *
FROM users;

-- query: get_all_current_presences
SELECT *
FROM presences
WHERE user_id = ANY($1);

-- query: get_all_old_presences
SELECT *
FROM old_presences
WHERE user_id = ANY($1);

-- query: check_joins
SELECT user_id
FROM presences
WHERE place_id = $1
AND game_instance_id = $2
AND NOT user_id = $3;