CREATE TABLE [gold].[dim_locations] (

	[Location Key] varchar(400) NULL, 
	[Location ID] int NULL, 
	[Location] varchar(8000) NULL, 
	[City] varchar(8000) NULL, 
	[Region] varchar(8000) NULL, 
	[Country Code (ISO)] varchar(8000) NULL, 
	[Country] varchar(8000) NULL, 
	[Loaded at (UTC)] datetime2(6) NULL
);