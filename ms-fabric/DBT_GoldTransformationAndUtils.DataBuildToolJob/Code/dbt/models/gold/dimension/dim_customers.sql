{{ 
    config(
        unique_key='"Customer Key"'
    )
}}

WITH raw_customer_enriched AS (

    SELECT * FROM {{ source('silver', 'raw_customer_enriched') }}

    {% if is_incremental() %}  
    WHERE "Loaded at (UTC)" > (SELECT MAX("Loaded at (UTC)") from {{ this }})
    {% endif %}

), distinction AS (

    SELECT DISTINCT
        "Customer ID",
        "Birthday Date",
        "First Name",
        "Last Name",
        "Full Name",
        "Last First Name",
        Gender,
        "Marital Status",
        Email,
        "Phone Number",
        "Children Amount",
        City,
        Country,
        "Postal Code",
        "Preferred Language",
        "Favorite Brand",
        "Sign Up Date",
        "Loaded at (UTC)"
    FROM
        raw_customer_enriched

), keyed AS (

    SELECT
        {{
            dbt_utils.generate_surrogate_key([
                '"Customer ID"'
            ]) 
        }} AS "Customer Key",
        "Customer ID",
        "Birthday Date",
        "First Name",
        "Last Name",
        "Full Name",
        "Last First Name",
        Gender,
        "Marital Status",
        Email,
        "Phone Number",
        "Children Amount",
        City,
        Country,
        "Postal Code",
        "Preferred Language",
        "Favorite Brand",
        "Sign Up Date",
        "Loaded at (UTC)"
    FROM
        distinction

), final AS (

    SELECT
        "Customer Key",
        "Customer ID",
        "Birthday Date",
        "First Name",
        "Last Name",
        "Full Name",
        "Last First Name",
        Gender,
        "Marital Status",
        Email,
        "Phone Number",
        "Children Amount",
        City,
        Country,
        "Postal Code",
        "Preferred Language",
        "Favorite Brand",
        "Sign Up Date",
        "Loaded at (UTC)"
    FROM
        keyed

)

SELECT * FROM final