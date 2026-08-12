CREATE TABLE [gold].[fact_order_details] (

	[Order Detail Key] varchar(400) NULL, 
	[Customer DBT SCD ID] varchar(32) NULL, 
	[Franchise Owner DBT SCD ID] varchar(32) NULL, 
	[Menu Item Key] varchar(400) NULL, 
	[Location Key] varchar(400) NULL, 
	[Truck Key] varchar(400) NULL, 
	[Order Detail ID] int NULL, 
	[Order ID] int NULL, 
	[Order Date] date NULL, 
	[Order Time] time(0) NULL, 
	[Quantity] int NULL, 
	[Unit Price (USD)] real NULL, 
	[Total Price (USD)] real NULL, 
	[Loaded at (UTC)] datetime2(6) NULL
);