f'''
    

    SELECT
        xele.vehicle_id AS vehicle_id
        links.link_id AS link_id
        xele.time AS time
        xple.enter AS enter
    FROM xml_events_leg_events AS xele
    LEFT JOIN links
    ON xple.link_str = links.link_str
    LEFT JOIN 
    ON (
        ve.vehicle_id = xele.vehicle_id AND


    )

    SELECT
        
    FROM vehicle_events as ve
    ORDER BY
        vehicle,
        time
'''