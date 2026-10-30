-- query: get_version
SELECT current_version
FROM metadata;

-- query: set_version
INSERT INTO metadata (id, current_version)
VALUES (1, $1)
ON CONFLICT (id)
DO UPDATE SET
    current_version = EXCLUDED.current_version;