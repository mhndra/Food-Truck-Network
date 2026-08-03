{{ 
    config(
        unique_key='"Menu Item Key"'
    )
}}

WITH menu_enriched AS (

    SELECT * FROM {{ source('silver', 'menu_enriched') }}

    {% if is_incremental() %}  
    WHERE "Loaded at (UTC)" > (SELECT MAX("Loaded at (UTC)") FROM {{ this }})
    {% endif %}

), distinction AS (

    SELECT DISTINCT
        "Menu Item ID",
        "Menu Item Name",
        "Menu Item Subcategory",
        "Menu Item Category",
        "Menu Type ID",
        "Menu Type",
        "Truck Brand Name",
        "COGS (USD)",
        "Selling Price (USD)",
        Ingredients,
        "Is Dairy Free",
        "Is Gluten Free",
        "Is Healthy",
        "Is Nut Free",
        "Loaded at (UTC)"
    FROM
        menu_enriched

), keyed AS (

    SELECT
        {{ 
            dbt_utils.generate_surrogate_key([
                '"Menu Item ID"'
            ])
        }} AS "Menu Item Key",
        "Menu Item ID",
        "Menu Item Name",
        "Menu Item Subcategory",
        "Menu Item Category",
        "Menu Type ID",
        "Menu Type",
        "Truck Brand Name",
        "COGS (USD)",
        "Selling Price (USD)",
        Ingredients,
        "Is Dairy Free",
        "Is Gluten Free",
        "Is Healthy",
        "Is Nut Free",
        "Loaded at (UTC)"
    FROM
        distinction

), final AS (

    SELECT
        "Menu Item Key",
        "Menu Item ID",
        "Menu Item Name",
        "Menu Item Subcategory",
        "Menu Item Category",
        "Menu Type ID",
        "Menu Type",
        "Truck Brand Name",
        "COGS (USD)",
        "Selling Price (USD)",
        Ingredients,
        "Is Dairy Free",
        "Is Gluten Free",
        "Is Healthy",
        "Is Nut Free",
        "Loaded at (UTC)"
    FROM
        keyed

)

SELECT * FROM final