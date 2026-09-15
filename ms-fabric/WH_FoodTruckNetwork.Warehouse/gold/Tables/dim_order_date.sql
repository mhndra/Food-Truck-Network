CREATE TABLE [gold].[dim_order_date] (

	[Order Date] date NULL, 
	[First Day of Week (ISO)] date NULL, 
	[Month Year] date NULL, 
	[Day] int NULL, 
	[Month] varchar(10) NULL, 
	[Quarter] varchar(5) NULL, 
	[Year] int NULL, 
	[Day of Week] varchar(9) NULL, 
	[Day of Week Sorting] int NULL
);