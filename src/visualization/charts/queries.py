f'''

SELECT
    ROUND(`time`, -3) AS `bucket`,
    COUNT(*) AS `frequency`,
    RPAD('', COUNT(*) / 100000, '*') AS `bar`
FROM icarus_postsim.routes
WHERE mode <= 4
GROUP BY bucket
LIMIT 20;

SELECT
    ROUND(`dur_time`, -3) AS `bucket`,
    COUNT(*) AS `frequency`,
    RPAD('', COUNT(*) / 100000, '*') AS `bar`
FROM icarus_presim.routes
WHERE mode <= 4
GROUP BY bucket
LIMIT 20;


SELECT
    bin,
    SUM(freq)
FROM(
    SELECT
        ROUND(`time`, -3) AS `bin`,
        COUNT(*) AS `freq`
    FROM icarus_postsim.vehicle_events
    WHERE enter = 1
    GROUP BY bin
    UNION
    SELECT
        ROUND(`time`, -3) AS `bin`,
        COUNT(*) * -1 AS `freq`
    FROM icarus_postsim.vehicle_events
    WHERE enter = 0
    GROUP BY bin
) AS temp
GROUP BY bin
LIMIT 50;

SELECT
    bin,
    SUM(freq)
FROM(
    SELECT
        ROUND(dep_time, -2) AS bin,
        COUNT(*) AS freq
    FROM icarus_presim.routes
    GROUP BY bin
    UNION
    SELECT
        ROUND(dep_time + dur_time, -2) AS bin,
        COUNT(*) * -1 AS freq
    FROM icarus_presim.routes
    GROUP BY bin
) AS temp
GROUP BY bin
LIMIT 50;

CREATE TABLE link_flow AS
SELECT
    link_str,
    COUNT(*) as flow_count
FROM xml_events_leg_events
WHERE enter = 1
GROUP BY link_str



'''