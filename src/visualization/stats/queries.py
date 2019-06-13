f'''

SELECT
    ROUND(`time`, -3) AS `bucket`,
    COUNT(*) AS `frequency`,
    RPAD('', COUNT(*) / 100000, '*') AS `bar`
FROM routes
GROUP BY bucket
LIMIT 20;

SELECT
    ROUND(`distance`, -4) AS `bucket`,
    COUNT(*) AS `frequency`,
    RPAD('', COUNT(*) / 50000, '*') AS `bar`
FROM routes
GROUP BY bucket
LIMIT 25;




















'''