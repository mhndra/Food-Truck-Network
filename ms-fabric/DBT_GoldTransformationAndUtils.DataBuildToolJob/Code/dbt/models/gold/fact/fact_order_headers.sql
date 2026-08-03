{{
    config(
        materialized='table'
    )
}}

WITH fact_order_details AS (

    SELECT * FROM {{ ref('fact_order_details') }}

), order_header_grouped AS (

    SELECT
        "Customer DBT SCD ID",
        "Franchise Owner DBT SCD ID",
        "Location Key",
        "Truck Key",
        "Order ID",
        "Order Date",
        "Order Time",
        COUNT("Order Detail ID") AS "Order Amount",
        SUM("Quantity") AS "Total Order Quantities",
        SUM("Total Price (USD)") AS "Total Order Price (USD)"
    FROM
        fact_order_details
    GROUP BY
        "Customer DBT SCD ID",
        "Franchise Owner DBT SCD ID",
        "Location Key",
        "Truck Key",
        "Order ID",
        "Order Date",
        "Order Time"

), keyed AS (

    SELECT
        {{ 
            dbt_utils.generate_surrogate_key([
                '"Order ID"'
            ])
        }} AS "Order Key",
        "Customer DBT SCD ID",
        "Franchise Owner DBT SCD ID",
        "Location Key",
        "Truck Key",
        "Order ID",
        "Order Date",
        "Order Time",
        "Order Amount",
        "Total Order Quantities",
        "Total Order Price (USD)"
    FROM
        order_header_grouped

), final AS (

    SELECT
        "Order Key",
        "Customer DBT SCD ID",
        "Franchise Owner DBT SCD ID",
        "Location Key",
        "Truck Key",
        "Order ID",
        "Order Date",
        "Order Time",
        "Order Amount",
        "Total Order Quantities",
        "Total Order Price (USD)"
    FROM
        keyed

)

SELECT * FROM final