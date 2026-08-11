{{
    config(
        unique_key='"Order Detail Key"'
    )
}}

WITH order_detail_renamed AS (

    SELECT * FROM {{ source('silver', 'order_detail_renamed') }}

    {% if is_incremental() %}  
    WHERE "Loaded at (UTC)" > (SELECT MAX("Loaded at (UTC)") FROM {{ this }})
    {% endif %}

), order_detail_enriched AS (

    SELECT
        d."Order Detail ID",
        d."Order ID",
        h."Customer ID",
        t."Franchise Owner ID",
        d."Menu Item ID",
        h."Location ID",
        h."Truck ID",
        CAST(h."Order Timestamp (NTZ)" AS DATE) AS "Order Date",
        CAST(h."Order Timestamp (NTZ)" AS TIME(0)) AS "Order Time",
        d."Quantity",
        d."Unit Price (USD)",
        d."Total Price (USD)",
        d."Loaded at (UTC)"
    FROM
        order_detail_renamed d
    JOIN
        {{ source('silver', 'order_header_renamed') }} h
    ON
        d."Order ID" = h."Order ID"
    JOIN
        {{ source('silver', 'truck_enriched') }} t
    ON
        h."Truck ID" = t."Truck ID"

), keyed AS (

    SELECT
        {{ 
            dbt_utils.generate_surrogate_key([
                '"Order Detail ID"',
                '"Order ID"',
                '"Customer ID"',
                '"Franchise Owner ID"',
                '"Menu Item ID"',
                '"Location ID"',
                '"Truck ID"',
                '"Order Date"',
                '"Order Time"',
            ])
        }} AS "Order Detail Key",
        "Order Detail ID",
        "Order ID",
        "Customer ID",
        "Franchise Owner ID",
        "Menu Item ID",
        "Location ID",
        "Truck ID",
        "Order Date",
        "Order Time",
        "Quantity",
        "Unit Price (USD)",
        "Total Price (USD)",
        "Loaded at (UTC)"
    FROM
        order_detail_enriched

), join_dimension_tables AS (

    SELECT
        k.*,
        c.dbt_scd_id AS "Customer DBT SCD ID",
        f.dbt_scd_id AS "Franchise Owner DBT SCD ID",
        m."Menu Item Key",
        l."Location Key",
        t."Truck Key"
    FROM
        keyed k
    LEFT JOIN 
        (SELECT * FROM {{ ref('dim_customers_snapshot') }} WHERE dbt_valid_to IS NULL) c
    ON
        k."Customer ID" = c."Customer ID"
    LEFT JOIN
        (SELECT * FROM {{ ref('dim_franchise_owners_snapshot') }} WHERE dbt_valid_to IS NULL) f
    ON
        k."Franchise Owner ID" = f."Franchise Owner ID"
    LEFT JOIN
        {{ ref('dim_menu_items') }} m
    ON
        k."Menu Item ID" = m."Menu Item ID"
    LEFT JOIN
        {{ ref('dim_locations') }} l
    ON
        k."Location ID" = l."Location ID"
    LEFT JOIN
        {{ ref('dim_trucks') }} t
    ON
        k."Truck ID" = t."Truck ID"
    
), final AS (

    SELECT
        "Order Detail Key",
        "Customer DBT SCD ID",
        "Franchise Owner DBT SCD ID",
        "Menu Item Key",
        "Location Key",
        "Truck Key",
        "Order Detail ID",
        "Order ID",
        "Order Date",
        "Order Time",
        "Quantity",
        "Unit Price (USD)",
        "Total Price (USD)",
        "Loaded at (UTC)"
    FROM
        join_dimension_tables

)

SELECT * FROM final


