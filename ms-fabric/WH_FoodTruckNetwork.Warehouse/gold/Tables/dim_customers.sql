CREATE TABLE [gold].[dim_customers] (

	[Customer Key] varchar(400) NULL, 
	[Customer ID] int NULL, 
	[Birthday Date] date NULL, 
	[First Name] varchar(8000) NULL, 
	[Last Name] varchar(8000) NULL, 
	[Full Name] varchar(8000) NULL, 
	[Last First Name] varchar(8000) NULL, 
	[Gender] varchar(8000) NULL, 
	[Marital Status] varchar(8000) NULL, 
	[Email] varchar(8000) NULL, 
	[Phone Number] varchar(8000) NULL, 
	[Children Amount] varchar(8000) NULL, 
	[City] varchar(8000) NULL, 
	[Country] varchar(8000) NULL, 
	[Postal Code] varchar(8000) NULL, 
	[Preferred Language] varchar(8000) NULL, 
	[Favorite Brand] varchar(8000) NULL, 
	[Sign Up Date] date NULL, 
	[Loaded at (UTC)] datetime2(6) NULL
);