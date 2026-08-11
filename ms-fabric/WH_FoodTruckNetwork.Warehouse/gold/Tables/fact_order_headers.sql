CREATE TABLE [gold].[fact_order_headers] (

	[Order Key] varchar(400) NULL, 
	[Customer DBT SCD ID] varchar(32) NULL, 
	[Franchise Owner DBT SCD ID] varchar(32) NULL, 
	[Location Key] varchar(400) NULL, 
	[Truck Key] varchar(400) NULL, 
	[Order ID] int NULL, 
	[Order Date] date NULL, 
	[Order Time] time(0) NULL, 
	[Order Amount] int NULL, 
	[Total Order Quantities] int NULL, 
	[Total Order Price (USD)] float NULL
);