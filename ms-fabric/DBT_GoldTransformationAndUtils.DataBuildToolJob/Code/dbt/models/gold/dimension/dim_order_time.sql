{{
    config(
        materialized='table'
    )
}}

WITH order_header_renamed AS (

    SELECT * FROM {{ source('silver', 'order_header_renamed') }}

), distinction AS (

    SELECT DISTINCT
        CAST("Order Timestamp (NTZ)" AS TIME(0)) AS "Order Time"
    FROM
        order_header_renamed

), time_enriched AS (

    SELECT
        "Order Time",
        DATEPART(second, "Order Time") AS Second,
        DATEPART(minute, "Order Time") AS Minute,
        DATEPART(hour, "Order Time") AS Hour,
        CAST(
            FORMAT(CAST("Order Time" AS DATETIME2), 'hh tt') 
            AS VARCHAR(5)
        ) AS "Hour of Day"
    FROM
        distinction

), final AS (

    SELECT
        "Order Time",
        Second,
        Minute,
        Hour,
        "Hour of Day"
    FROM
        time_enriched

)

SELECT * FROM final