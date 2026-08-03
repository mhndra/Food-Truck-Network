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