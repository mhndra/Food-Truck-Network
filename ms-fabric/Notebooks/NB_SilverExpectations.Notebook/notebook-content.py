# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "55312fb3-148f-459a-be62-fa4a63a5902f",
# META       "default_lakehouse_name": "LH_FoodTruckNetwork",
# META       "default_lakehouse_workspace_id": "542bda20-f3f2-43f7-a24d-8b502233b148",
# META       "known_lakehouses": [
# META         {
# META           "id": "55312fb3-148f-459a-be62-fa4a63a5902f"
# META         }
# META       ]
# META     },
# META     "environment": {
# META       "environmentId": "7c8f3501-81d2-852f-4339-3a31c72af024",
# META       "workspaceId": "00000000-0000-0000-0000-000000000000"
# META     }
# META   }
# META }

# MARKDOWN ********************

# # Data Quality in Silver Layer Using Great Expectations 

# MARKDOWN ********************

# ## 00 Importing packages

# CELL ********************

import great_expectations as gx
import great_expectations.expectations as gxe
from pyspark.sql.functions import *

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 01 Creating functions

# CELL ********************

def run_expectations(context, table_name:str, dataframe):
    # Get or add data_sources
    try:
        data_source = context.data_sources.get(
            name="spark_source"
        )
    except:
        data_source = context.data_sources.add_spark(
            name="spark_source"
        )

    # Get or add asset
    try:
        data_asset = data_source.get_asset(
            name=f"{table_name}_asset"
        )
    except:
        data_asset = data_source.add_dataframe_asset(
            name=f"{table_name}_asset"
        )

    # Get or add batch_definition
    try:
        batch_definition = data_asset.get_batch_definition(
            name=f"{table_name}_batch_def"
        )
    except:
        batch_definition = data_asset.add_batch_definition_whole_dataframe(
            name=f"{table_name}_batch_def"
        )
    
    # Get or add validation_definition
    try:
        validation_definition = context.validation_definitions.get(
            name=f"{table_name}_validation"
        )
    except:
        suite = context.suites.get(
            name=f"{table_name}_suite"
        )
        validation_definition = context.validation_definitions.add(
            gx.ValidationDefinition(
                name=f"{table_name}_validation",
                data=batch_definition,
                suite=suite
            )
        )
    
    # Add or update checkpoint
    checkpoint = context.checkpoints.add_or_update(
        gx.Checkpoint(
            name=f"{table_name}_checkpoint",
            validation_definitions=[validation_definition],
            actions=[gx.checkpoint.UpdateDataDocsAction(name="update_data_docs")]
        )
    )

    # Run checkpoint
    print(f"Running {table_name}_checkpoint")
    result = checkpoint.run(
        batch_parameters={
            "dataframe": dataframe
        }
    )
    print(f"===> Successfuly running: {result.success}\n")
    
    # Generate expectations failed summary
    validation_result = list(result.run_results.values())[0]
    if not validation_result["success"]:
        failed_summary = {}

        # Get suite name
        failed_summary["suite"] = validation_definition.suite.name

        # Get column name, expectation, and result
        failed_summary["details"] = []
        for result in validation_result["results"]:
            if not result["success"]:
                failed_summary["details"].append({
                    "column": result["expectation_config"]["kwargs"]["column"],
                    "expectation": result["expectation_config"]["type"],
                    "result": {
                        "element_count": result["result"]["element_count"],
                        "unexpected_count": result["result"]["unexpected_count"],
                        "partial_unexpected_counts": result["result"]["partial_unexpected_counts"]
                    }
                })

        raise Exception(f"===> Expectations failed:{failed_summary}\n")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 02 Getting gx context in silver layer

# CELL ********************

# Define gx context
context = gx.get_context(
    mode="file",
    project_root_dir="/lakehouse/default/Files/silver_gx"
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 03 Get or add suites and their expectations

# MARKDOWN ********************

# ### 03-1 silver.franchise_cleaned table

# CELL ********************

franchise_cleaned_df = spark.read.table("silver.franchise_cleaned")
franchise_cleaned_df_exploded = franchise_cleaned_df.withColumn(
    "Franchise City",
    explode(from_json("Franchise City Grouped", "array<string>"))
).drop("Franchise City Grouped")
display(franchise_cleaned_df_exploded.count())
franchise_cleaned_df_exploded.createOrReplaceTempView("franchise_exploded")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC SELECT
# MAGIC     COLLECT_SET(`Franchise Owner ID`),
# MAGIC     COLLECT_SET(`Franchise Owner First Name`),
# MAGIC     COLLECT_SET(`Franchise Owner Last Name`),
# MAGIC     COLLECT_SET(`Franchise Owner Email`),
# MAGIC     COLLECT_SET(`Franchise Owner Phone Number`),
# MAGIC     COLLECT_SET(`Franchise City`),
# MAGIC     COLLECT_SET(`Franchise Country`),
# MAGIC     COLLECT_SET(`Franchise Owner Full Name`),
# MAGIC     COLLECT_SET(`Franchise Owner Last First Name`)
# MAGIC FROM
# MAGIC     franchise_exploded

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Define franchise_cleaned_suite

# CELL ********************

try:
    franchise_cleaned_suite = context.suites.get(
        name="franchise_cleaned_suite"
    )
    franchise_cleaned_suite.expectations = []
    franchise_cleaned_suite.save()
except:
    franchise_cleaned_suite = context.suites.add(
        gx.ExpectationSuite(
            name="franchise_cleaned_suite"
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to not be null

# CELL ********************

for column in franchise_cleaned_df_exploded.columns:
    franchise_cleaned_suite.add_expectation(
        gxe.ExpectColumnValuesToNotBeNull(
            column=column
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to match regex

# CELL ********************

name_pattern = r"[A-Za-z'-]+"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Franchise owner first name column
franchise_cleaned_suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegex(
        column="Franchise Owner First Name",
        regex=f"^{name_pattern}$"
    )
)

# Franchise owner last name column
franchise_cleaned_suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegex(
        column="Franchise Owner Last Name",
        regex=f"^{name_pattern}$"
    )
)

# Franchise owner full name column
franchise_cleaned_suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegex(
        column="Franchise Owner Full Name",
        regex=f"^{name_pattern} {name_pattern}$"
    )
)

# Franchise owner last first column
franchise_cleaned_suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegex(
        column="Franchise Owner Last First Name",
        regex=f"^{name_pattern}, {name_pattern}$"
    )
)

# Franchise owner email column
franchise_cleaned_suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegex(
        column="Franchise Owner Email",
        regex=r".*@.*\..*"
    )    
)

# Franchise owner phone number column
franchise_cleaned_suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegex(
        column="Franchise Owner Phone Number",
        regex=r"^[0-9]{3}-[0-9]{3}-[0-9]{4}$"
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to be in set

# CELL ********************

city_names = [
    "Vancouver",
    "Madrid",
    "Cairo",
    "New York City",
    "Munich",
    "Sao Paulo",
    "Manchester",
    "Montreal",
    "Tokyo",
    "Seattle",
    "Toronto",
    "Denver",
    "Warsaw",
    "Berlin",
    "Delhi",
    "Mumbai",
    "Seoul",
    "London",
    "San Mateo",
    "Paris",
    "Krakow",
    "Nice",
    "Rio de Janeiro",
    "Melbourne",
    "Barcelona",
    "Boston",
    "Cape Town",
    "Sydney",
    "Hamburg",
    "Stockholm"
]
country_names = [
    "Poland",
    "Spain",
    "Sweden",
    "Australia",
    "Canada",
    "South Africa",
    "India",
    "Japan",
    "England",
    "Egypt",
    "Germany",
    "South Korea",
    "Brazil",
    "France",
    "United States",
    "United Kingdom"
]

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Franchise city column
franchise_cleaned_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Franchise City",
        value_set=city_names
    )
)

# Franchise country column
franchise_cleaned_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Franchise Country",
        value_set=country_names
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

franchise_cleaned_suite.save()
print("Total expectations:", len(franchise_cleaned_suite.expectations))
display(franchise_cleaned_suite)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 03-2 silver.location_enriched table

# CELL ********************

location_enriched_df = spark.read.table("silver.location_enriched")
location_enriched_df.createOrReplaceTempView("location_enriched")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC SELECT
# MAGIC     COLLECT_SET(Location),
# MAGIC     MAX(LENGTH(Location)),
# MAGIC     COLLECT_SET(City),
# MAGIC     COLLECT_SET(`Country Code (ISO)`),
# MAGIC     COLLECT_SET(Country),
# MAGIC     COLLECT_SET(Region)
# MAGIC FROM
# MAGIC     location_enriched

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Define location_enriched_suite

# CELL ********************

try:
    location_enriched_suite = context.suites.get(
        name="location_enriched_suite"
    )
    location_enriched_suite.expectations = []
    location_enriched_suite.save()
except:
    location_enriched_suite = context.suites.add(
        gx.ExpectationSuite(
            name="location_enriched_suite"
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to not be null

# CELL ********************

for column in location_enriched_df.columns:
    location_enriched_suite.add_expectation(
        gxe.ExpectColumnValuesToNotBeNull(
            column=column
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to be unique

# CELL ********************

# Location ID column
location_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeUnique(
        column="`Location ID`"
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column value lengths to be between

# CELL ********************

# Location column
location_enriched_suite.add_expectation(
    gxe.ExpectColumnValueLengthsToBeBetween(
        column="Location", 
        min_value=1, 
        max_value=200
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to be in set

# CELL ********************

country_codes = [
    "GB",
    "BR",
    "KR",
    "FR",
    "SE",
    "AU",
    "JP",
    "ZA",
    "PL",
    "CA",
    "DE",
    "ES",
    "US",
    "IN",
    "EG"
]

region_names = ["Other", "EMEA", "North America", "APAC"]

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# City column
location_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="City",
        value_set=city_names
    )
)

# Country code (ISO) column
location_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Country Code (ISO)",
        value_set=country_codes
    )
)

# Country column
location_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Country",
        value_set=country_names
    )
)

# Region column
location_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Region",
        value_set=region_names
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

location_enriched_suite.save()
print("Total expectations:", len(location_enriched_suite.expectations))
display(location_enriched_suite)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 03-3 silver.menu_enriched table

# CELL ********************

menu_enriched_df = spark.read.table("silver.menu_enriched")
menu_enriched_df.createOrReplaceTempView("menu_enriched")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC SELECT
# MAGIC     COLLECT_SET(`Menu Item Name`),
# MAGIC     MAX(LENGTH(`Menu Item Name`)),
# MAGIC     COLLECT_SET(`Menu Item Subcategory`),
# MAGIC     COLLECT_SET(`Menu Item Category`),
# MAGIC     COLLECT_SET(`Menu Type ID`),
# MAGIC     COLLECT_SET(`Menu Type`),
# MAGIC     COLLECT_SET(`Truck Brand Name`),
# MAGIC     MIN(`COGS (USD)`),
# MAGIC     MAX(`COGS (USD)`),
# MAGIC     MIN(`Selling Price (USD)`),
# MAGIC     MAX(`Selling Price (USD)`),
# MAGIC     COLLECT_SET(`Is Dairy Free`),
# MAGIC     COLLECT_SET(`Is Gluten Free`),
# MAGIC     COLLECT_SET(`Is Healthy`),
# MAGIC     COLLECT_SET(`Is Nut Free`)
# MAGIC FROM
# MAGIC     menu_enriched

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Define menu_enriched_suite

# CELL ********************

try:
    menu_enriched_suite = context.suites.get(
        name="menu_enriched_suite"
    )
    menu_enriched_suite.expectations = []
    menu_enriched_suite.save()
except:
    menu_enriched_suite = context.suites.add(
        gx.ExpectationSuite(
            name="menu_enriched_suite"
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to not be null

# CELL ********************

for column in menu_enriched_df.columns:
    menu_enriched_suite.add_expectation(
        gxe.ExpectColumnValuesToNotBeNull(
            column=column
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to be unique

# CELL ********************

# Menu item ID column
menu_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeUnique(
        column="`Menu Item ID`"
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to match regex

# CELL ********************

# Menu type ID column
menu_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegex(
        column="Menu Type ID",
        regex=r"^[1-9]{1}[0-9]{0,1}$"
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column value lengths to be between

# CELL ********************

# Menu item name column
menu_enriched_suite.add_expectation(
    gxe.ExpectColumnValueLengthsToBeBetween(
        column="`Menu Item Name`", 
        min_value=1, 
        max_value=100
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to be between

# CELL ********************

# COGS (USD) and selling price (USD) columns
usd_columns = [column for column in menu_enriched_df.columns if "USD" in column]
for column in usd_columns:
    menu_enriched_suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(
            column=column,
            min_value=0.1
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column pair values A to be greater than B

# CELL ********************

# COGS (USD) column pair with selling price (USD) column
menu_enriched_suite.add_expectation(
    gxe.ExpectColumnPairValuesAToBeGreaterThanB(
        column_A="Selling Price (USD)",
        column_B="COGS (USD)"
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to be in set

# CELL ********************

# Menu item subcategory column
menu_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Menu Item Subcategory",
        value_set=["Hot Option","Cold Option","Warm Option"]
    )
)

# Menu item category column
menu_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Menu Item Category",
        value_set=["Main","Dessert","Beverage","Snack"]
    )
)

# Menu type column
menu_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Menu Type",
        value_set=[
            "Chinese",
            "Indian",
            "Crepes",
            "Hot Dogs",
            "Ice Cream",
            "Ramen",
            "Grilled Cheese",
            "Tacos",
            "Mac & Cheese",
            "Poutine",
            "Sandwiches",
            "BBQ",
            "Gyros",
            "Vegetarian",
            "Ethiopian"
        ]
    )
)

# Truck brand name column
menu_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Truck Brand Name",
        value_set=[
            "Nani's Kitchen",
            "Smoky BBQ",
            "Cheeky Greek",
            "Le Coin des Crêpes",
            "Freezing Point",
            "Better Off Bread",
            "Peking Truck",
            "Guac n' Roll",
            "Revenge of the Curds",
            "Amped Up Franks",
            "Tasty Tibs",
            "The Mega Melt",
            "Kitakata Ramen Bar",
            "Plant Palace",
            "The Mac Shack"
        ]
    )
)

# Is dairy free, is gluten free, is healthy, is nut free columns
is_columns = [column for column in menu_enriched_df.columns if "Is" in column]
for column in is_columns:
    menu_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column=column,
        value_set=["No", "Yes"]
    )
)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

menu_enriched_suite.save()
print("Total expectations:", len(menu_enriched_suite.expectations))
display(menu_enriched_suite)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 03-4 silver.order_detail_renamed table

# CELL ********************

order_detail_renamed_df = spark.read.table("silver.order_detail_renamed")
order_detail_renamed_df.createOrReplaceTempView("order_detail_renamed")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC SELECT
# MAGIC     MIN(`Order ID`),
# MAGIC     MAX(`Order ID`),
# MAGIC     MIN(`Menu Item ID`),
# MAGIC     MAX(`Menu Item ID`),
# MAGIC     MIN(Quantity),
# MAGIC     MAX(Quantity),
# MAGIC     MIN(`Unit Price (USD)`),
# MAGIC     MAX(`Unit Price (USD)`),
# MAGIC     MIN(`Total Price (USD)`),
# MAGIC     MAX(`Total Price (USD)`)
# MAGIC FROM
# MAGIC     order_detail_renamed

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Define order_detail_renamed_suite

# CELL ********************

try:
    order_detail_renamed_suite = context.suites.get(
        name="order_detail_renamed_suite"
    )
    order_detail_renamed_suite.expectations = []
    order_detail_renamed_suite.save()
except:
    order_detail_renamed_suite = context.suites.add(
        gx.ExpectationSuite(
            name="order_detail_renamed_suite"
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to not be null

# CELL ********************

for column in order_detail_renamed_df.columns:
    order_detail_renamed_suite.add_expectation(
        gxe.ExpectColumnValuesToNotBeNull(
            column=column
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to be unique

# CELL ********************

# Order detail ID column
order_detail_renamed_suite.add_expectation(
    gxe.ExpectColumnValuesToBeUnique(
        column="`Order Detail ID`"
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values lengths to be between

# CELL ********************

# Order ID column
order_detail_renamed_suite.add_expectation(
    gxe.ExpectColumnValueLengthsToBeBetween(
        column="`Order ID`", 
        min_value=7, 
        max_value=9
    )
)

# Menu item ID column
order_detail_renamed_suite.add_expectation(
    gxe.ExpectColumnValueLengthsToBeBetween(
        column="`Menu Item ID`", 
        min_value=2, 
        max_value=3
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to be between

# CELL ********************

# Quantity column
order_detail_renamed_suite.add_expectation(
    gxe.ExpectColumnValuesToBeBetween(
        column="Quantity",
        min_value=1
    )
)

# Unit price (USD) and total price (USD) columns
price_usd_columns = [column for column in order_detail_renamed_df.columns if "USD" in column]
for column in price_usd_columns:
    order_detail_renamed_suite.add_expectation(
        gxe.ExpectColumnValuesToBeBetween(
            column=column,
            min_value=2
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

order_detail_renamed_suite.save()
print("Total expectations:", len(order_detail_renamed_suite.expectations))
display(order_detail_renamed_suite)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 03-5 silver.order_header_renamed table

# CELL ********************

order_header_renamed_df = spark.read.table("silver.order_header_renamed")
order_header_renamed_df.createOrReplaceTempView("order_header_renamed")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC SELECT
# MAGIC     MIN(`Truck ID`),
# MAGIC     MAX(`Truck ID`),
# MAGIC     MIN(`Location ID`),
# MAGIC     MAX(`Location ID`),
# MAGIC     MIN(`Customer ID`),
# MAGIC     MAX(`Customer ID`)
# MAGIC FROM
# MAGIC     order_header_renamed

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Define order_header_renamed_suite

# CELL ********************

try:
    order_header_renamed_suite = context.suites.get(
        name="order_header_renamed_suite"
    )
    order_header_renamed_suite.expectations = []
    order_header_renamed_suite.save()
except:
    order_header_renamed_suite = context.suites.add(
        gx.ExpectationSuite(
            name="order_header_renamed_suite"
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to not be null

# CELL ********************

for column in order_header_renamed_df.columns:
    order_header_renamed_suite.add_expectation(
        gxe.ExpectColumnValuesToNotBeNull(
            column=column
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to be unique

# CELL ********************

# Order ID column
order_header_renamed_suite.add_expectation(
    gxe.ExpectColumnValuesToBeUnique(
        column="`Order ID`"
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column value lengths to be between

# CELL ********************

# Truck ID column
order_header_renamed_suite.add_expectation(
    gxe.ExpectColumnValueLengthsToBeBetween(
        column="`Truck ID`", 
        min_value=1, 
        max_value=3
    )
)

# Location ID column
order_header_renamed_suite.add_expectation(
    gxe.ExpectColumnValueLengthsToBeBetween(
        column="`Location ID`", 
        min_value=4, 
        max_value=5
    )
)

# Customer ID column
order_header_renamed_suite.add_expectation(
    gxe.ExpectColumnValueLengthsToBeBetween(
        column="`Customer ID`", 
        min_value=1, 
        max_value=6
    )
)


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

order_header_renamed_suite.save()
print("Total expectations:", len(order_header_renamed_suite.expectations))
display(order_header_renamed_suite)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 03-6 silver.raw_customer_enriched table

# CELL ********************

raw_customer_enriched_df = spark.read.table("silver.raw_customer_enriched")
raw_customer_enriched_df.createOrReplaceTempView("raw_customer_enriched")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC SELECT
# MAGIC     COLLECT_SET(`First Name`),
# MAGIC     COLLECT_SET(`Last Name`),
# MAGIC     COLLECT_SET(Gender),
# MAGIC     COLLECT_SET(`Marital Status`),
# MAGIC     COLLECT_SET(Email),
# MAGIC     COLLECT_SET(`Phone Number`),
# MAGIC     COLLECT_SET(`Children Amount`),
# MAGIC     COLLECT_SET(City),
# MAGIC     COLLECT_SET(Country),
# MAGIC     COLLECT_SET(`Postal Code`),
# MAGIC     MAX(LENGTH(`Postal Code`)),
# MAGIC     COLLECT_SET(`Preferred Language`),
# MAGIC     COLLECT_SET(`Favorite Brand`),
# MAGIC     COLLECT_SET(`Full Name`),
# MAGIC     COLLECT_SET(`Last First Name`)
# MAGIC 
# MAGIC FROM
# MAGIC     raw_customer_enriched

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Define raw_customer_enriched_suite

# CELL ********************

try:
    raw_customer_enriched_suite = context.suites.get(
        name="raw_customer_enriched_suite"
    )
    raw_customer_enriched_suite.expectations = []
    raw_customer_enriched_suite.save()
except:
    raw_customer_enriched_suite = context.suites.add(
        gx.ExpectationSuite(
            name="raw_customer_enriched_suite"
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to not be null

# CELL ********************

for column in raw_customer_enriched_df.columns:
    raw_customer_enriched_suite.add_expectation(
        gxe.ExpectColumnValuesToNotBeNull(
            column=column
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to be unique

# CELL ********************

# Customer ID column
raw_customer_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeUnique(
        column="`Customer ID`"
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to match regex

# CELL ********************

# First name column
raw_customer_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegex(
        column="First Name",
        regex=f"^{name_pattern}$"
    )
)

# Last name column
raw_customer_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegex(
        column="Last Name",
        regex=f"^{name_pattern}$"
    )
)

# Email column
raw_customer_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegex(
        column="Email",
        regex=r".*@.*\..*"
    )    
)

# Phone number column
raw_customer_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegex(
        column="Phone Number",
        regex=r"^\d{3}-\d{3}-\d{4}$"
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to match regex list

# CELL ********************

postal_code_pattern = r"^[A-Za-z0-9 ]+$"

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Postal code column
raw_customer_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegexList(
        column="Postal Code", 
        regex_list=[
            r"\d{2,5}-\d{3,4}",
            r"\d{2}-\d{1}",
            postal_code_pattern
        ], 
        match_on="any"
    )
)

# Full name column
raw_customer_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegexList(
        column="Full Name",
        regex_list=[
            f"^{name_pattern} {name_pattern}$",
            f"^{name_pattern}$"
        ],
        match_on="any"
    )
)

# Last first column
raw_customer_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegexList(
        column="Last First Name",
        regex_list=[
            f"^{name_pattern}, {name_pattern}$",
            f"^{name_pattern}$"
        ],
        match_on="any"
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to be in set

# CELL ********************

# Gender column
raw_customer_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Gender",
        value_set=["Male","Female","Undisclosed"]
    )
)

# Marital status column
raw_customer_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Marital Status",
        value_set=[
            "Single",
            "Divorced/Seperated",
            "Married",
            "Undisclosed"
        ]
    )
)

# Children amount column
raw_customer_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Children Amount",
        value_set=[
            "1",
            "3",
            "4",
            "5+",
            "2",
            "Undisclosed",
            "0"
        ]
    )
)

# City column
raw_customer_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="City",
        value_set=city_names
    )
)

# Country column
raw_customer_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Country",
        value_set=country_names
    )
)

# Preferrend language column
raw_customer_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Preferred Language",
        value_set=[
            "German",
            "Portuguese",
            "Korean",
            "Hindi",
            "Polish",
            "Swedish",
            "French",
            "Spanish",
            "English",
            "Japanese",
            "Arabic"
        ]
    )
)

# Favorite brand column
raw_customer_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Favorite Brand",
        value_set=["Undisclosed"]
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

raw_customer_enriched_suite.save()
print("Total expectations:", len(raw_customer_enriched_suite.expectations))
display(raw_customer_enriched_suite)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 03-7 silver.truck_enriched table

# CELL ********************

truck_enriched_df = spark.read.table("silver.truck_enriched")
truck_enriched_df.createOrReplaceTempView("truck_enriched")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC SELECT
# MAGIC     MIN(`Menu Type ID`),
# MAGIC     MAX(`Menu Type ID`),
# MAGIC     MIN(`Franchise Owner ID`),
# MAGIC     MAX(`Franchise Owner ID`),
# MAGIC     COLLECT_SET(Manufacturer),
# MAGIC     COLLECT_SET(Model),
# MAGIC     COLLECT_SET(City),
# MAGIC     COLLECT_SET(`Region Code (ISO)`),
# MAGIC     COLLECT_SET(Region),
# MAGIC     COLLECT_SET(`Country Code (ISO)`),
# MAGIC     COLLECT_SET(Country),
# MAGIC     COLLECT_SET(`Opening Year`),
# MAGIC     COLLECT_SET(`Is Franchise Flag`),
# MAGIC     COLLECT_SET(`Is EV Flag`),
# MAGIC     MIN(`Operating Age`),
# MAGIC     MAX(`Operating Age`)
# MAGIC 
# MAGIC FROM
# MAGIC     truck_enriched

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Define truck_enriched_suite

# CELL ********************

try:
    truck_enriched_suite = context.suites.get(
        name="truck_enriched_suite"
    )
    truck_enriched_suite.expectations = []
    truck_enriched_suite.save()
except:
    truck_enriched_suite = context.suites.add(
        gx.ExpectationSuite(
            name="truck_enriched_suite"
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to not be null

# CELL ********************

for column in truck_enriched_df.columns:
    truck_enriched_suite.add_expectation(
        gxe.ExpectColumnValuesToNotBeNull(
            column=column
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to be unique

# CELL ********************

# Truck ID column
truck_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeUnique(
        column="`Truck ID`"
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to match regex

# CELL ********************

# Menu type ID column
truck_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegex(
        column="Menu Type ID",
        regex=r"^[1-9]{1}[0-9]{0,1}$"
    )
)

# Franchise owner ID column
truck_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToMatchRegex(
        column="Franchise Owner ID",
        regex=r"^[1-9]{1}[0-9]{0,2}$"
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to be between

# CELL ********************

# Opening year column
truck_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeBetween(
        column="Opening Year",
        min_value=1970
    )
)

# Operating age column
truck_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeBetween(
        column="Operating Age",
        min_value=1
    )
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# #### > Column values to be in set

# CELL ********************

# Manufacturer column
truck_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Manufacturer",
        value_set=[
            "Airstream",
            "Citroën",
            "Ford",
            "Chevrolet",
            "Custom",
            "Freightliner",
            "Volkswagen",
            "Nissan"
        ]
    )
)

# Model column
truck_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Model",
        value_set=[
            "Van",
            "P30",
            "H Van",
            "Step Van",
            "Trailer",
            "Box Truck",
            "NV 2500 High Roof",
            "MT45 Utilimaster",
            "Westfalia Bus"
        ]
    )
)

# City column
truck_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="City",
        value_set=city_names
    )
)

# Region code (ISO) column
truck_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Region code (ISO)",
        value_set=[
            "Victoria",
            "Greater London",
            "Madrid",
            "Western Cape",
            "Lesser Poland",
            "WA",
            "CA",
            "Tokyo",
            "Berlin",
            "Al Qahirah",
            "NY",
            "Delhi",
            "Seoul",
            "Masovian",
            "BC",
            "New South Wales",
            "QC",
            "Greater Manchester",
            "Paris",
            "ON",
            "Rio de Janeiro",
            "Barcelona",
            "Maharashtra",
            "Alpes-Maritimes",
            "Bayern",
            "CO",
            "Hamburg",
            "Stockholm",
            "MA",
            "São Paulo"
        ]
    )
)

# Region column
truck_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Region",
        value_set=[
            "Victoria",
            "Greater London",
            "Kantō",
            "California",
            "Western Cape",
            "Provence–Alpes–Côte-d'Azur",
            "Brandenburg",
            "Cairo Governorate",
            "British Columbia",
            "Małopolskie województwo",
            "Barcelona provincia",
            "Île-de-France",
            "New York",
            "Colorado",
            "Washington",
            "Quebec",
            "São Paulo estado",
            "Rio de Janeiro, estado ",
            "Delhi",
            "Bavaria",
            "New South Wales",
            "Greater Manchester",
            "Seoul Capital",
            "Mazowieckie województwo",
            "Maharashtra",
            "Madrid provincia",
            "Ontario",
            "Hamburg",
            "Stockholm, län",
            "Massachusetts"
        ]
    )
)

# Country code (ISO) column
truck_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Country Code (ISO)",
        value_set=country_codes
    )
)

# Country column
truck_enriched_suite.add_expectation(
    gxe.ExpectColumnValuesToBeInSet(
        column="Country",
        value_set=country_names
    )
)

# Is franchise flag and is EV flag columns
flag_columns = [column for column in truck_enriched_df.columns if "Flag" in column]
for column in flag_columns:
    truck_enriched_suite.add_expectation(
        gxe.ExpectColumnValuesToBeInSet(
            column=column,
            value_set=[0, 1]
        )
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

truck_enriched_suite.save()
print("Total expectations:", len(truck_enriched_suite.expectations))
display(truck_enriched_suite)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 04 Running expectations each table

# CELL ********************

references = [
    ("franchise_cleaned", franchise_cleaned_df_exploded),
    ("location_enriched", location_enriched_df),
    ("menu_enriched", menu_enriched_df),
    ("order_detail_renamed", order_detail_renamed_df),
    ("order_header_renamed", order_header_renamed_df),
    ("raw_customer_enriched", raw_customer_enriched_df),
    ("truck_enriched", truck_enriched_df)
]

for table_name, dataframe in references:
    run_expectations(
        context=context,
        table_name=table_name,
        dataframe=dataframe
    )

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

notebookutils.session.stop()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
