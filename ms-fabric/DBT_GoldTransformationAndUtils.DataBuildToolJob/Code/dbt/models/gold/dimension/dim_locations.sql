{{ 
    config(
        unique_key='"Location Key"'
    )
}}

WITH location_enriched AS (

    SELECT * FROM {{ source('silver', 'location_enriched') }}

    {% if is_incremental() %}  
    WHERE "Loaded at (UTC)" > (SELECT MAX("Loaded at (UTC)") FROM {{ this }})
    {% endif %}

), distinction AS (

    SELECT DISTINCT
        "Location ID",
        "Location",
        "City",
        "Region",
        "Country Code (ISO)",
        "Country",
        "Loaded at (UTC)"
    FROM
        location_enriched

), keyed AS (

    SELECT
        {{ 
            dbt_utils.generate_surrogate_key([
                '"Location ID"'
            ])
        }} AS "Location Key",
        "Location ID",
        "Location",
        "City",
        "Region",
        "Country Code (ISO)",
        "Country",
        "Loaded at (UTC)"
    FROM
        distinction

), final AS (

    SELECT
        "Location Key",
        "Location ID",
        "Location",
        "City",
        "Region",
        "Country Code (ISO)",
        "Country",
        "Loaded at (UTC)"
    FROM
        keyed

)

SELECT * FROM final