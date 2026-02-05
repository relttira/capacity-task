from sqlmodel import text


CAPACITY = text(
    """
        WITH UniqueVoyages AS (
            SELECT 
                service_version_and_roundtrip_identfiers,
                origin_service_version_and_master,
                destination_service_version_and_master,
                MAX(origin_at_utc) AS latest_departure,
                offered_capacity_teu
            FROM SailingLevelRaw
            WHERE origin = 'china_main' 
                AND destination = 'north_europe_main'
            GROUP BY 
                service_version_and_roundtrip_identfiers,
                origin_service_version_and_master,
                destination_service_version_and_master
        ),
        WeeklyAggregates AS (
            SELECT 
                date(latest_departure, 'weekday 0', '-6 days') AS week_start_date,
                CAST(strftime('%W', latest_departure) AS INTEGER) AS week_no,
                SUM(offered_capacity_teu) AS weekly_sum
            FROM UniqueVoyages
            GROUP BY week_start_date
        )
        SELECT 
            week_start_date,
            week_no,
            CAST(AVG(weekly_sum) OVER (
                ORDER BY week_start_date 
                ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
            ) AS INTEGER) AS offered_capacity_teu
        FROM WeeklyAggregates
        WHERE week_start_date BETWEEN :date_from AND :date_to
        ORDER BY week_start_date;
    """
)
