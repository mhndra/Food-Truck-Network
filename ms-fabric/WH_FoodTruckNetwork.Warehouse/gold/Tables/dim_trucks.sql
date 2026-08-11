CREATE TABLE [gold].[dim_trucks] (

	[Truck Key] varchar(400) NULL, 
	[Truck ID] int NULL, 
	[Franchise Owner ID] int NULL, 
	[Truck Brand Name] varchar(8000) NULL, 
	[Manufacturer] varchar(8000) NULL, 
	[Model] varchar(8000) NULL, 
	[City] varchar(8000) NULL, 
	[Region Code (ISO)] varchar(8000) NULL, 
	[Region] varchar(8000) NULL, 
	[Country Code (ISO)] varchar(8000) NULL, 
	[Country] varchar(8000) NULL, 
	[Opening Year] int NULL, 
	[Operating Age] int NULL, 
	[Is Franchise Flag] int NULL, 
	[Is EV Flag] int NULL, 
	[Loaded at (UTC)] datetime2(6) NULL
);