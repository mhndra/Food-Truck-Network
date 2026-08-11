CREATE TABLE [gold].[dim_franchise_owners_snapshot] (

	[Franchise Owner Key] varchar(400) NULL, 
	[Franchise Owner ID] int NULL, 
	[Franchise Owner First Name] varchar(8000) NULL, 
	[Franchise Owner Last Name] varchar(8000) NULL, 
	[Franchise Owner Full Name] varchar(8000) NULL, 
	[Franchise Owner Last First Name] varchar(8000) NULL, 
	[Franchise Owner Email] varchar(8000) NULL, 
	[Franchise Owner Phone Number] varchar(8000) NULL, 
	[Franchise City Grouped] varchar(8000) NULL, 
	[Franchise Country] varchar(8000) NULL, 
	[Loaded at (UTC)] datetime2(6) NULL, 
	[dbt_scd_id] varchar(32) NULL, 
	[dbt_updated_at] datetime2(6) NULL, 
	[dbt_valid_from] datetime2(6) NULL, 
	[dbt_valid_to] datetime2(6) NULL
);