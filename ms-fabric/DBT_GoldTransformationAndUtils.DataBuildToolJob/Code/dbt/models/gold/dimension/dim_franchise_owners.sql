{{
    config(
        unique_key='"Franchise Owner Key"'
    )
}}

WITH franchise_cleaned AS (

    SELECT * FROM {{ source('silver', 'franchise_cleaned') }} n

    {% if is_incremental() %}  
    WHERE "Loaded at (UTC)" > (SELECT MAX("Loaded at (UTC)") FROM {{ this }})
    -- AND
    -- (
    --     City > (
    --         SELECT MAX(City)
    --         FROM {{ this }} f 
    --         WHERE f."Franchise Owner ID" = n."Franchise Owner ID"
    --     )
    --     OR NOT EXISTS (
    --         SELECT 1 
    --         FROM {{ this }} f
    --         WHERE f."Franchise Owner ID" = n."Franchise Owner ID"
    --     )
    -- )
    {% endif %}

), distinction AS (

    SELECT DISTINCT
        "Franchise Owner ID",
        "Franchise Owner First Name",
        "Franchise Owner Last Name",
        "Franchise Owner Full Name",
        "Franchise Owner Last First Name",
        "Franchise Owner Email",
        "Franchise Owner Phone Number",
        "Franchise City Grouped",
        "Franchise Country",
        -- ROW_NUMBER() OVER(PARTITION BY "Franchise Owner ID" ORDER BY City) AS rn,
        "Loaded at (UTC)"
    FROM
        franchise_cleaned

), keyed AS (

    SELECT
        {{ 
            dbt_utils.generate_surrogate_key([
                '"Franchise Owner ID"'
            ]) 
        }} AS "Franchise Owner Key",
        "Franchise Owner ID",
        "Franchise Owner First Name",
        "Franchise Owner Last Name",
        "Franchise Owner Full Name",
        "Franchise Owner Last First Name",
        "Franchise Owner Email",
        "Franchise Owner Phone Number",
        "Franchise City Grouped",
        "Franchise Country",
        "Loaded at (UTC)"
    FROM
        distinction
    -- WHERE
    --     rn = 1

), final AS (

    SELECT
        "Franchise Owner Key",
        "Franchise Owner ID",
        "Franchise Owner First Name",
        "Franchise Owner Last Name",
        "Franchise Owner Full Name",
        "Franchise Owner Last First Name",
        "Franchise Owner Email",
        "Franchise Owner Phone Number",
        "Franchise City Grouped",
        "Franchise Country",
        "Loaded at (UTC)"
    FROM
        keyed

)

SELECT * FROM final