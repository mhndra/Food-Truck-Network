CREATE TABLE [gold].[dim_menu_items] (

	[Menu Item Key] varchar(400) NULL, 
	[Menu Item ID] varchar(8000) NULL, 
	[Menu Item Name] varchar(8000) NULL, 
	[Menu Item Subcategory] varchar(8000) NULL, 
	[Menu Item Category] varchar(8000) NULL, 
	[Menu Type ID] int NULL, 
	[Menu Type] varchar(8000) NULL, 
	[Truck Brand Name] varchar(8000) NULL, 
	[COGS (USD)] real NULL, 
	[Selling Price (USD)] real NULL, 
	[Ingredients] varchar(8000) NULL, 
	[Is Dairy Free] varchar(8000) NULL, 
	[Is Gluten Free] varchar(8000) NULL, 
	[Is Healthy] varchar(8000) NULL, 
	[Is Nut Free] varchar(8000) NULL, 
	[Loaded at (UTC)] datetime2(6) NULL
);