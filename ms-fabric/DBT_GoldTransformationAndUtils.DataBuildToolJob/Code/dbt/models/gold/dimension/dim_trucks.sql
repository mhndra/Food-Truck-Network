{{
    config(
        unique_key='"Truck Key"'
    )
}}

WITH truck_enriched AS (

    SELECT * FROM {{ source('silver', 'truck_enriched') }}

    {% if is_incremental() %}  
    WHERE "Loaded at (UTC)" > (SELECT MAX("Loaded at (UTC)") FROM {{ this }})
    {% endif %}

), join_menu_enriched AS (

    SELECT
        t.*,
        m."Truck Brand Name"
    FROM
        truck_enriched t
    JOIN
        {{ source('silver', 'menu_enriched') }} m
    ON
        t."Menu Type ID" = m."Menu Type ID"

), distinction AS (

    SELECT DISTINCT
        "Truck ID",
        "Franchise Owner ID",
        "Truck Brand Name",
        "Manufacturer",
        "Model",
        "City",
        "Region Code (ISO)",
        "Region",
        "Country Code (ISO)",
        "Country",
        "Opening Year",
        "Operating Age",
        "Is Franchise Flag",
        "Is EV Flag",
        "Loaded at (UTC)"
    FROM
        join_menu_enriched

), keyed AS (

    SELECT
        {{ 
            dbt_utils.generate_surrogate_key([
                '"Truck ID"'
            ]) 
        }} AS "Truck Key",
        "Truck ID",
        "Franchise Owner ID",
        "Truck Brand Name",
        "Manufacturer",
        "Model",
        "City",
        "Region Code (ISO)",
        "Region",
        "Country Code (ISO)",
        "Country",
        "Opening Year",
        "Operating Age",
        "Is Franchise Flag",
        "Is EV Flag",
        "Loaded at (UTC)"
    FROM
        distinction

), final AS (

    SELECT
        "Truck Key",
        "Truck ID",
        "Franchise Owner ID",
        "Truck Brand Name",
        "Manufacturer",
        "Model",
        "City",
        "Region Code (ISO)",
        "Region",
        "Country Code (ISO)",
        "Country",
        "Opening Year",
        "Operating Age",
        "Is Franchise Flag",
        "Is EV Flag",
        "Loaded at (UTC)"
    FROM
        keyed

)

SELECT * FROM final