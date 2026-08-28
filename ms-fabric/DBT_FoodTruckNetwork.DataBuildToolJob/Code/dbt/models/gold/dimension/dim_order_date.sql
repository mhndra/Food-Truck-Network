{{
    config(
        materialized='table'
    )
}}

WITH order_header_renamed AS (

    SELECT * FROM {{ source('silver', 'order_header_renamed') }}

), distinction AS (

    SELECT DISTINCT
        CAST("Order Timestamp (NTZ)" AS DATE) AS "Order Date"
    FROM
        order_header_renamed

), date_enriched AS (

    SELECT
        "Order Date",
        DAY("Order Date") AS Day,
        CAST(
            DATENAME(month, "Order Date") 
            AS VARCHAR(10)
        ) AS Month,
        CAST(
            'Qtr ' + CAST(DATEPART(quarter, "Order Date") AS VARCHAR(1))
            AS VARCHAR(5)
        ) AS Quarter,
        YEAR("Order Date") AS Year,
        CAST(
            DATENAME(weekday, "Order Date") 
            AS VARCHAR(9)
        ) AS "Day of Week",
        DATEPART(weekday, "Order Date") AS "Day of Week Sorting",
        -- CAST(
        --     DATENAME(month, "Order Date") + ' ' + DATENAME(year, "Order Date") 
        --     AS VARCHAR(15)
        -- ) AS "Month Year",
        -- DENSE_RANK() OVER(ORDER BY YEAR("Order Date"), MONTH("Order Date")) AS "Month Year Sorting"
        DATETRUNC(month, "Order Date") AS "Month Year"
    FROM
        distinction

), final AS (

    SELECT
        "Order Date",
        Day,
        Month,
        Quarter,
        Year,
        "Day of Week",
        "Day of Week Sorting",
        "Month Year"
    FROM
        date_enriched

)

SELECT * FROM final