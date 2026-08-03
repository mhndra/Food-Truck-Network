-- Fabric notebook source

-- METADATA ********************

-- META {
-- META   "kernel_info": {
-- META     "name": "sqldatawarehouse"
-- META   },
-- META   "dependencies": {
-- META     "warehouse": {
-- META       "default_warehouse": "73d1a354-3cf9-8d7f-4949-89f0314e6aae",
-- META       "known_warehouses": [
-- META         {
-- META           "id": "73d1a354-3cf9-8d7f-4949-89f0314e6aae",
-- META           "type": "Datawarehouse"
-- META         }
-- META       ]
-- META     }
-- META   }
-- META }

-- MARKDOWN ********************

-- # WH_FoodTruckNetwork Warehouse Security

-- MARKDOWN ********************

-- ## 00 GRANT and DENY objects to user

-- MARKDOWN ********************

-- ### > GRANT permission

-- CELL ********************

GRANT SELECT ON SCHEMA :: [gold] TO [EMEA], [North America], [APAC];

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- MARKDOWN ********************

-- ### > DENY permission

-- CELL ********************

DENY SELECT ON [gold].[dim_customers] TO [EMEA], [North America], [APAC];
DENY SELECT ON [gold].[dim_franchise_owners] TO [EMEA], [North America], [APAC];
-- DENY SELECT ON [gold].[dim_customers_snapshot]([Birthday Date]) TO [EMEA], [North America], [APAC];

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

SELECT 
    pr.name AS user_name,
    perm.state_desc,
    perm.permission_name,
    CASE perm.class
        WHEN 0 THEN 'DATABASE'
        WHEN 3 THEN 'SCHEMA'
        WHEN 1 THEN 'OBJECT'
        ELSE perm.class_desc
    END AS target_type,
    CASE perm.class
        WHEN 0 THEN DB_NAME()
        WHEN 3 THEN SCHEMA_NAME(perm.major_id)
        WHEN 1 THEN 
            OBJECT_SCHEMA_NAME(perm.major_id) + '.' + OBJECT_NAME(perm.major_id)
            + CASE WHEN perm.minor_id != 0 
                   THEN '.' + COL_NAME(perm.major_id, perm.minor_id) 
                   ELSE '' 
              END
        ELSE CAST(perm.major_id AS VARCHAR)
    END AS target_name
FROM sys.database_permissions perm
JOIN sys.database_principals pr 
    ON perm.grantee_principal_id = pr.principal_id
WHERE pr.name != 'public';

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- MARKDOWN ********************

-- ## 01 Row-level security

-- CELL ********************

DROP SECURITY POLICY IF EXISTS YourSecurityPolicy;
DROP FUNCTION IF EXISTS [Security].[tvf_securitypredicate];
GO

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

CREATE FUNCTION Security.tvf_securitypredicate(@region AS VARCHAR(100))
    RETURNS TABLE
WITH SCHEMABINDING
AS
    RETURN 
    SELECT 1 AS tvf_securitypredicate_result
    WHERE 
        EXISTS (
            SELECT 1 
            FROM [Security].[user_region_mapping]
            WHERE userPrincipalName = USER_NAME()
            AND region = @region
    )
    OR 
        USER_NAME() IN ('zynerta@zohomail.eu', 'topimhn@zohomail.eu');
GO

CREATE SECURITY POLICY YourSecurityPolicy
ADD FILTER PREDICATE Security.tvf_securitypredicate(Region)
ON [gold].[dim_locations]
WITH (STATE = ON);
GO


-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- MARKDOWN ********************

-- ## 02 Dynamic data masking

-- MARKDOWN ********************

-- ### > Masking name columns

-- CELL ********************

ALTER TABLE [gold].[dim_customers_snapshot]
ALTER COLUMN [First Name] ADD MASKED WITH (FUNCTION = 'partial(0, "**~MASKED~**", 0)');
ALTER TABLE [gold].[dim_customers_snapshot]
ALTER COLUMN [Last Name] ADD MASKED WITH (FUNCTION = 'partial(0, "**~MASKED~**", 0)');
ALTER TABLE [gold].[dim_customers_snapshot]
ALTER COLUMN [Full Name] ADD MASKED WITH (FUNCTION = 'partial(0, "**~MASKED~**", 0)');
ALTER TABLE [gold].[dim_customers_snapshot]
ALTER COLUMN [Last First Name] ADD MASKED WITH (FUNCTION = 'partial(0, "**~MASKED~**", 0)');

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- MARKDOWN ********************

-- ### > Masking a email column

-- CELL ********************

ALTER TABLE [gold].[dim_customers_snapshot]
ALTER COLUMN [Email] ADD MASKED WITH (FUNCTION = 'partial(0, "**~MASKED~**.**~MASKED~**@hotmail.com
", 0)');

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- MARKDOWN ********************

-- ### > Masking a phone number column

-- CELL ********************

ALTER TABLE [gold].[dim_customers_snapshot]
ALTER COLUMN [Phone Number] ADD MASKED WITH (FUNCTION = 'partial(0, "111-111-1111", 0)');

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- MARKDOWN ********************

-- ### Masking a date of birth column

-- CELL ********************

ALTER TABLE [gold].[dim_customers_snapshot]
ALTER COLUMN [Birthday Date] ADD MASKED WITH (FUNCTION = 'default()');

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************

SELECT 
    c.name AS column_name,
    tbl.name AS table_name,
    OBJECT_SCHEMA_NAME(tbl.object_id) AS schema_name,
    c.is_masked,
    c.masking_function
FROM sys.masked_columns AS c
JOIN sys.tables AS tbl 
    ON c.[object_id] = tbl.[object_id]
WHERE c.is_masked = 1;

-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }

-- CELL ********************


-- METADATA ********************

-- META {
-- META   "language": "sql",
-- META   "language_group": "sqldatawarehouse"
-- META }
