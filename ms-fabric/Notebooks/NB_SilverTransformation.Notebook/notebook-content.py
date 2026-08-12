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

# # Data Transformation in Silver Layer

# MARKDOWN ********************

# ## 00 Importing packages

# CELL ********************

from pyspark.sql.functions import *
from pyspark.sql.types import *
from delta.tables import *

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 01 Creating functions

# CELL ********************

def loading_enriched_table(df_source, target_table, candidate_key):
    try:
        deltaTable = DeltaTable.forName(spark, target_table)
    except Exception:
        try:
            df_source.write.format("delta").option("delta.columnMapping.mode", "name").saveAsTable(f"{target_table}")
        except Exception as e:
            print(f":Load for table {target_table} failed with error: {str(e)}")
            raise
        return
    
    try:
        match_condition = " AND ".join([f"target.`{col}` = source.`{col}`" for col in candidate_key])

        target_columns = deltaTable.toDF().columns
        new_columns = [col for col in df_source.columns if col not in candidate_key and col not in target_columns]

        if new_columns:
            backfill_expressions = {col: f"source.`{col}`" for col in new_columns}
            deltaTable.alias("target").merge(
                source=df_source.alias("source"),
                condition=match_condition
            ).whenMatchedUpdate(
                set=backfill_expressions
            ).withSchemaEvolution().execute()

            deltaTable = DeltaTable.forName(spark, target_table)

        change_detection_columns = [col for col in df_source.columns if col not in candidate_key]
        update_condition = " OR ".join([f"target.`{col}` != source.`{col}`" for col in change_detection_columns])
        update_expressions = {col: f"source.`{col}`" for col in df_source.columns}

        deltaTable.alias("target").merge(
            source=df_source.alias("source"),
            condition=match_condition
        ).whenMatchedUpdate(
            condition=update_condition,
            set=update_expressions
        ).whenNotMatchedInsertAll().withSchemaEvolution().execute()
        
    except Exception as e:
        print(f"Insert operation for table {target_table} failed with error: {str(e)}")
    return

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 02 Data transformation for silver.franchise_cleaned table

# MARKDOWN ********************

# ### 02-1 Getting data from bronze.franchise table

# CELL ********************

franchise_df = spark.read.table("bronze.franchise")

display(franchise_df.limit(10))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# - Handling missing values

# CELL ********************

display(franchise_df.select([count(when(col(column).isNull(), column)).alias(column) for column in franchise_df.columns]))
print("Total rows: ", franchise_df.count())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 02-2 Renaming columns from franchise_df DataFrame

# CELL ********************

franchise_df_renamed = franchise_df.select(
    col("Column1").cast(IntegerType()).alias("Franchise Owner ID"),
    col("Column2").alias("Franchise Owner First Name"),
    col("Column3").alias("Franchise Owner Last Name"),
    col("Column6").alias("Franchise Owner Email"),
    col("Column7").alias("Franchise Owner Phone Number"),
    col("Column4").alias("Franchise City"),
    col("Column5").alias("Franchise Country"),
    col("Loaded at").cast(TimestampType()).alias("Loaded at (UTC)")
)

display(franchise_df_renamed.limit(10))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

franchise_df_renamed.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 02-3 Adding combined columns from franchise_df_renamed DataFrame

# CELL ********************

franchise_df_enriched = franchise_df_renamed.withColumn(
    "Franchise Owner Full Name",
    concat_ws(
        " ", 
        col("Franchise Owner First Name"), 
        col("Franchise Owner Last Name")
    )
).withColumn(
    "Franchise Owner Last First Name",
    concat_ws(
        ", ",
        col("Franchise Owner Last Name"),
        col("Franchise Owner First Name")
    )
)

display(franchise_df_enriched.limit(10))
print("Total rows: ", franchise_df_enriched.count())
print("Total distinct rows: ", franchise_df_enriched.distinct().count())
print("Total distinct natural key rows: ", franchise_df_enriched.select("Franchise Owner ID").distinct().count())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

franchise_df_enriched.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# - Handling duplicate values on natural key

# CELL ********************

franchise_df_enriched.createOrReplaceTempView("franchise_enriched")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC SELECT
# MAGIC     `Franchise Owner ID`,
# MAGIC     COUNT(DISTINCT `Franchise Owner First Name`),
# MAGIC     COUNT(DISTINCT `Franchise Owner Last Name`),
# MAGIC     COUNT(DISTINCT `Franchise Owner Email`),
# MAGIC     COUNT(DISTINCT `Franchise Owner Phone Number`),
# MAGIC     COUNT(DISTINCT `Franchise Country`),
# MAGIC     COUNT(DISTINCT `Franchise City`),
# MAGIC     COLLECT_SET(`Franchise City`),
# MAGIC     COUNT(DISTINCT `Franchise Owner Full Name`),
# MAGIC     COUNT(DISTINCT `Franchise Owner Last First Name`)
# MAGIC FROM
# MAGIC     franchise_enriched
# MAGIC GROUP BY
# MAGIC     `Franchise Owner ID`
# MAGIC HAVING
# MAGIC     COUNT(DISTINCT `Franchise Owner First Name`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Franchise Owner Last Name`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Franchise Owner Email`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Franchise Owner Phone Number`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Franchise Country`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Franchise City`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Franchise Owner Full Name`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Franchise Owner Last First Name`) > 1

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 02-4 Grouping nested values for handling duplicate values on natural key

# CELL ********************

franchise_df_grouped = franchise_df_enriched.groupBy(
    "Franchise Owner ID",
    "Franchise Owner First Name",
    "Franchise Owner Last Name",
    "Franchise Owner Email",
    "Franchise Owner Phone Number",
    "Franchise Country",
    "Loaded at (UTC)",
    "Franchise Owner Full Name",
    "Franchise Owner Last First Name"
).agg(
    collect_set("Franchise City").alias("Franchise City Array")
).withColumn(
    "Franchise City Grouped",
    to_json("Franchise City Array")
)

display(franchise_df_grouped.limit(10))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

franchise_df_grouped.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 02-5 Removing duplicate values from franchise_df_renamed DataFrame

# CELL ********************

franchise_df_cleaned = franchise_df_grouped.drop(
    "Franchise City",
    "Franchise City Array"
).dropDuplicates()

print("Total rows: ", franchise_df_cleaned.count())
print("Total distinct rows: ", franchise_df_cleaned.distinct().count())
print("Total distinct natural key rows: ", franchise_df_cleaned.select("Franchise Owner ID").distinct().count())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

franchise_df_cleaned.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 02-6 Loading franchise_df_cleaned DataFrame into silver.franchise_cleaned table

# CELL ********************

loading_enriched_table(
    df_source=franchise_df_cleaned,
    target_table="silver.franchise_cleaned",
    candidate_key=["Franchise Owner ID"]
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 03 Data transformation for silver.location_enriched table

# MARKDOWN ********************

# ### 03-1 Getting data from bronze.location table

# CELL ********************

location_df = spark.read.table("bronze.location")

display(location_df.limit(10))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# - Handling missing values

# CELL ********************

display(location_df.select([count(when(col(column).isNull(), column)).alias(column) for column in location_df.columns]))
print("Total rows: ", location_df.count())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 03-2 Renaming columns from location_df DataFrame

# CELL ********************

location_df_renamed = location_df.select(
    col("Column1").cast(IntegerType()).alias("Location ID"),
    col("Column3").alias("Location"),
    col("Column4").alias("City"),
    col("Column6").alias("Country Code (ISO)"),
    col("Column7").alias("Country"),
    col("Loaded at").cast(TimestampType()).alias("Loaded at (UTC)")
)

display(location_df_renamed.limit(10))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

location_df_renamed.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 03-3 Adding conditional columns to location_df_renamed DataFrame

# CELL ********************

location_df_enriched = location_df_renamed.withColumn(
    "Region",
    when(
        col("Country").isin("England", "France", "Germany", "Poland", "Spain", "Sweden"),
        lit("EMEA")
    ).when(
        col("Country").isin("Canada", "Mexico", "United States"),
        lit("North America")
    ).when(
        col("Country").isin("Australia", "India", "Japan", "South Korea"),
        lit("APAC")
    ).otherwise(
        lit("Other")
    )
)

display(location_df_enriched.limit(10))
print("Total rows: ", location_df_enriched.count())
print("Total distinct rows: ", location_df_enriched.distinct().count())
print("Total distinct natural key rows: ", location_df_enriched.select("Location ID").distinct().count())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

location_df_enriched.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# - Handling duplicate values on natural key

# CELL ********************

location_df_enriched.createOrReplaceTempView("location_enriched")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC SELECT
# MAGIC     `Location ID`,
# MAGIC     COUNT(DISTINCT Location),
# MAGIC     COUNT(DISTINCT City),
# MAGIC     COUNT(DISTINCT `Country Code (ISO)`),
# MAGIC     COUNT(DISTINCT Country),
# MAGIC     COUNT(DISTINCT Region)
# MAGIC FROM
# MAGIC     location_enriched
# MAGIC GROUP BY
# MAGIC     `Location ID`
# MAGIC HAVING
# MAGIC     COUNT(DISTINCT Location) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT City) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Country Code (ISO)`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT Country) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT Region) > 1

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 03-4 Loading location_df_enriched DataFrame into silver.location_enriched table

# CELL ********************

loading_enriched_table(
    df_source=location_df_enriched,
    target_table="silver.location_enriched",
    candidate_key=["Location ID"]
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 04 Data transformation for silver.menu_enriched table

# MARKDOWN ********************

# ### 04-1 Getting data from bronze.menu table

# CELL ********************

menu_df = spark.read.table("bronze.menu")

display(menu_df.limit(10))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# - Handling missing values

# CELL ********************

display(menu_df.select([count(when(col(column).isNull(), column)).alias(column) for column in menu_df.columns]))
print("Total rows: ", menu_df.count())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 04-2 Renaming columns from menu_df DataFrame

# CELL ********************

menu_df_renamed = menu_df.select(
    col("Column5").alias("Menu Item ID"),
    col("Column6").alias("Menu Item Name"),
    col("Column8").alias("Menu Item Subcategory"),
    col("Column7").alias("Menu Item Category"),
    col("Column2").cast(IntegerType()).alias("Menu Type ID"),
    col("Column3").alias("Menu Type"),
    col("Column4").alias("Truck Brand Name"),
    col("Column9").cast(FloatType()).alias("COGS (USD)"),
    col("Column10").cast(FloatType()).alias("Selling Price (USD)"),
    parse_json(col("Column11")).alias("Menu Item Health Metrics"),
    col("Loaded at").cast(TimestampType()).alias("Loaded at (UTC)")
)

display(menu_df_renamed.limit(10))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

menu_df_renamed.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 04-3 Parsing semi-structured columns from menu_df_renamed DataFrame

# CELL ********************

menu_df_enriched = menu_df_renamed.withColumn(
    "Ingredients",
    variant_get(
        col("Menu Item Health Metrics"), 
        "$.menu_item_health_metrics[0].ingredients",
        "string"
    )
).withColumn(
    "Is Dairy Free",
    when(
        variant_get(
            col("Menu Item Health Metrics"), 
            "$.menu_item_health_metrics[0].is_dairy_free_flag", 
            "string"
        ) == "Y",
        lit("Yes")
    ).otherwise(
        lit("No")
    )
).withColumn(
    "Is Gluten Free",
    when(
        variant_get(
            col("Menu Item Health Metrics"), 
            "$.menu_item_health_metrics[0].is_gluten_free_flag", 
            "string"
        ) == "Y",
        lit("Yes")
    ).otherwise(
        lit("No")
    )
).withColumn(
    "Is Healthy",
    when(
        variant_get(
            col("Menu Item Health Metrics"), 
            "$.menu_item_health_metrics[0].is_healthy_flag", 
            "string"
        ) == "Y",
        lit("Yes")
    ).otherwise(
        lit("No")
    )
).withColumn(
    "Is Nut Free",
    when(
        variant_get(
            col("Menu Item Health Metrics"), 
            "$.menu_item_health_metrics[0].is_nut_free_flag", 
            "string"
        ) == "Y",
        lit("Yes")
    ).otherwise(
        lit("No")
    )
).drop("Menu Item Health Metrics")

display(menu_df_enriched.limit(10))
print("Total rows: ", menu_df_enriched.count())
print("Total distinct rows: ", menu_df_enriched.distinct().count())
print("Total distinct natural key rows: ", menu_df_enriched.select("Menu Item ID").distinct().count())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

menu_df_enriched.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# - Handling duplicate values on natural key

# CELL ********************

menu_df_enriched.createOrReplaceTempView("menu_enriched")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC SELECT
# MAGIC     `Menu Item ID`,
# MAGIC     COUNT(DISTINCT `Menu Item Name`),
# MAGIC     COUNT(DISTINCT `Menu Item Subcategory`),
# MAGIC     COUNT(DISTINCT `Menu Item Category`),
# MAGIC     COUNT(DISTINCT `Menu Type ID`),
# MAGIC     COUNT(DISTINCT `Menu Type`),
# MAGIC     COUNT(DISTINCT `Truck Brand Name`),
# MAGIC     COUNT(DISTINCT `COGS (USD)`),
# MAGIC     COUNT(DISTINCT `Selling Price (USD)`),
# MAGIC     COUNT(DISTINCT `Ingredients`),
# MAGIC     COUNT(DISTINCT `Is Dairy Free`),
# MAGIC     COUNT(DISTINCT `Is Gluten Free`),
# MAGIC     COUNT(DISTINCT `Is Healthy`),
# MAGIC     COUNT(DISTINCT `Is Nut Free`)
# MAGIC FROM
# MAGIC     menu_enriched
# MAGIC GROUP BY
# MAGIC     `Menu Item ID`
# MAGIC HAVING
# MAGIC     COUNT(DISTINCT `Menu Item Name`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Menu Item Subcategory`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Menu Item Category`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Menu Type ID`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Menu Type`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Truck Brand Name`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `COGS (USD)`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Selling Price (USD)`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Ingredients`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Is Dairy Free`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Is Gluten Free`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Is Healthy`) > 1
# MAGIC OR
# MAGIC     COUNT(DISTINCT `Is Nut Free`) > 1

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 04-4 Loading menu_df_enriched DataFrame into silver.menu_enriched table

# CELL ********************

loading_enriched_table(
    df_source=menu_df_enriched,
    target_table="silver.menu_enriched",
    candidate_key=["Menu Item ID"]
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 05 Data transformation for silver.order_detail_renamed table

# MARKDOWN ********************

# ### 05-1 Getting data from bronze.order_detail table

# CELL ********************

order_detail_df = spark.read.table("bronze.order_detail")

display(order_detail_df.limit(10))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# - Handling missing values

# CELL ********************

display(order_detail_df.select([count(when(col(column).isNull(), column)).alias(column) for column in order_detail_df.columns]))
print("Total rows: ", order_detail_df.count())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 05-2 Renaming columns from order_detail_df DataFrame

# CELL ********************

order_detail_df_renamed = order_detail_df.select(
    col("Column1").cast(IntegerType()).alias("Order Detail ID"),
    col("Column2").cast(IntegerType()).alias("Order ID"),
    col("Column3").cast(IntegerType()).alias("Menu Item ID"),
    col("Column6").cast(IntegerType()).alias("Quantity"),
    col("Column7").cast(FloatType()).alias("Unit Price (USD)"),
    col("Column8").cast(FloatType()).alias("Total Price (USD)"),
    col("Loaded at").cast(TimestampType()).alias("Loaded at (UTC)")
)

display(order_detail_df_renamed.limit(10))
print("Total rows: ", order_detail_df_renamed.count())
print("Total distinct rows: ", order_detail_df_renamed.distinct().count())
print("Total distinct natural key rows: ", order_detail_df_renamed.select("Order Detail ID").distinct().count())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

order_detail_df_renamed.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# - Handling duplicate values on natural key

# CELL ********************

order_detail_df_renamed.createOrReplaceTempView("order_detail_renamed")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC WITH natural_key_counts AS (
# MAGIC     SELECT 
# MAGIC         `Order Detail ID`, 
# MAGIC         COUNT(*) AS Count
# MAGIC     FROM
# MAGIC         order_detail_renamed
# MAGIC     GROUP BY
# MAGIC         `Order Detail ID`
# MAGIC     HAVING
# MAGIC         COUNT(*) > 1
# MAGIC )
# MAGIC SELECT
# MAGIC     o.`Order Detail ID`,
# MAGIC     SIZE(COLLECT_SET(o.`Order ID`)),
# MAGIC     SIZE(COLLECT_SET(o.`Menu Item ID`)),
# MAGIC     SIZE(COLLECT_SET(o.`Quantity`)),
# MAGIC     SIZE(COLLECT_SET(o.`Unit Price (USD)`)),
# MAGIC     SIZE(COLLECT_SET(o.`Total Price (USD)`))
# MAGIC FROM
# MAGIC     order_detail_renamed o
# MAGIC JOIN
# MAGIC     natural_key_counts
# MAGIC USING
# MAGIC     (`Order Detail ID`)
# MAGIC GROUP BY
# MAGIC     o.`Order Detail ID`
# MAGIC HAVING
# MAGIC     SIZE(COLLECT_SET(o.`Order ID`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(o.`Menu Item ID`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(o.`Quantity`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(o.`Unit Price (USD)`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(o.`Total Price (USD)`)) > 1

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 05-3 Loading order_detail_df_renamed DataFrame into silver.order_detail_renamed table

# CELL ********************

loading_enriched_table(
    df_source=order_detail_df_renamed,
    target_table="silver.order_detail_renamed",
    candidate_key=["Order Detail ID"]
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 06 Data transformation for silver.order_header_renamed table

# MARKDOWN ********************

# ### 06-1 Getting data from bronze.order_header table

# CELL ********************

order_header_df = spark.read.table("bronze.order_header")

display(order_header_df.limit(10))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# - Handling missing values

# CELL ********************

display(order_header_df.select([count(when(col(column).isNull(), column)).alias(column) for column in order_header_df.columns]))
print("Total rows: ", order_header_df.count())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 06-2 Renaming columns from order_header_df DataFrame

# CELL ********************

order_header_df_renamed = order_header_df.where(
    col("Column4").isNotNull()
).select(
    col("Column1").cast(IntegerType()).alias("Order ID"),
    col("Column2").cast(IntegerType()).alias("Truck ID"),
    col("Column3").cast(IntegerType()).alias("Location ID"),
    col("Column4").cast(IntegerType()).alias("Customer ID"),
    col("Column10").cast(TimestampType()).alias("Order Timestamp (NTZ)")
)

display(order_header_df_renamed.limit(10))
print("Total rows: ", order_header_df_renamed.count())
print("Total distinct rows: ", order_header_df_renamed.distinct().count())
print("Total distinct natural key rows: ", order_header_df_renamed.select("Order ID").distinct().count())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# - Handling duplicate values on natural key

# CELL ********************

order_header_df_renamed.createOrReplaceTempView("order_header_renamed")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC WITH natural_key_counts AS (
# MAGIC     SELECT 
# MAGIC         `Order ID`, 
# MAGIC         COUNT(*) AS Count
# MAGIC     FROM
# MAGIC         order_header_renamed
# MAGIC     GROUP BY
# MAGIC         `Order ID`
# MAGIC     HAVING
# MAGIC         COUNT(*) > 1
# MAGIC )
# MAGIC SELECT
# MAGIC     o.`Order ID`,
# MAGIC     SIZE(COLLECT_SET(`Truck ID`)),
# MAGIC     SIZE(COLLECT_SET(`Location ID`)),
# MAGIC     SIZE(COLLECT_SET(`Customer ID`))
# MAGIC FROM
# MAGIC     order_header_renamed o
# MAGIC JOIN
# MAGIC     natural_key_counts
# MAGIC USING
# MAGIC     (`Order ID`)
# MAGIC GROUP BY
# MAGIC     o.`Order ID`
# MAGIC HAVING
# MAGIC     SIZE(COLLECT_SET(`Truck ID`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Location ID`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Customer ID`)) > 1

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 06-3 Loading order_header_df_renamed DataFrame into silver.order_header_renamed table

# CELL ********************

loading_enriched_table(
    df_source=order_header_df_renamed,
    target_table="silver.order_header_renamed",
    candidate_key=["Order ID"]
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 07 Data transformation for silver.raw_customer_enriched table

# MARKDOWN ********************

# ### 07-1 Getting data from bronze.raw_customer table

# CELL ********************

raw_customer_df = spark.read.table("bronze.raw_customer")

display(raw_customer_df.limit(10))
display(raw_customer_df.where(col("Column15").contains("ARRAY_CONSTRAIN")).limit(10))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# - Handling missing values

# CELL ********************

display(raw_customer_df.select([count(when(col(column).isNull(), column)).alias(column) for column in raw_customer_df.columns]))
print("Total rows: ", raw_customer_df.count())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 07-2 Renaming columns from raw_customer_df DataFrame

# CELL ********************

raw_customer_df_renamed = raw_customer_df.select(
    col("Column1").cast(IntegerType()).alias("Customer ID"),
    col("Column13").cast(DateType()).alias("Birthday Date"),
    # Handling missing values on first name column
    coalesce(col("Column2"), lit("Guest")).alias("First Name"),
    col("Column3").alias("Last Name"),
    col("Column8").alias("Gender"),
    col("Column10").alias("Marital Status"),
    col("Column14").alias("Email"),
    # Replacing values on phone number column
    when(
        col("Column15").contains("ARRAY_CONSTRAIN"),
        lit("111-111-1111")
    ).otherwise(
        col("Column15")
    ).alias("Phone Number"),
    col("Column11").alias("Children Amount"),
    col("Column4").alias("City"),
    col("Column5").alias("Country"),
    # Handling missing values on postal code column 
    coalesce(col("Column6"), lit("Undisclosed")).alias("Postal Code"),
    col("Column7").alias("Preferred Language"),
    # Handling missing values on favorite brand column
    coalesce(col("Column9"), lit("Undisclosed")).alias("Favorite Brand"),
    col("Column12").cast(DateType()).alias("Sign Up Date"),
    col("Loaded at").cast(TimestampType()).alias("Loaded at (UTC)")
)

display(raw_customer_df_renamed.limit(10))
display(raw_customer_df_renamed.where(col("Phone Number").contains("ARRAY_CONSTRAIN")))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

raw_customer_df_renamed.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 07-3 Adding combined columns to raw_customer_df_renamed DataFrame

# CELL ********************

raw_customer_df_enriched = raw_customer_df_renamed.withColumn(
    "Full Name",
    concat_ws(
        " ", 
        nullif(col("First Name"), lit("Guest")), 
        col("Last Name")
    )
).withColumn(
    "Last First Name",
    concat_ws(
        ", ",
        col("Last Name"),
        nullif(col("First Name"), lit("Guest"))
    )
)

display(raw_customer_df_enriched.where(col("First Name").isin("Guest")).limit(10))
print("Total rows: ", raw_customer_df_enriched.count())
print("Total distinct rows: ", raw_customer_df_enriched.distinct().count())
print("Total distinct natural key rows: ", raw_customer_df_enriched.select("Customer ID").distinct().count())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

raw_customer_df_enriched.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# - Handling duplicate values on natural key

# CELL ********************

raw_customer_df_enriched.createOrReplaceTempView("raw_customer_enriched")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC WITH natural_key_counts AS (
# MAGIC     SELECT 
# MAGIC         `Customer ID`, 
# MAGIC         COUNT(*) AS Count
# MAGIC     FROM
# MAGIC         raw_customer_enriched
# MAGIC     GROUP BY
# MAGIC         `Customer ID`
# MAGIC     HAVING
# MAGIC         COUNT(*) > 1
# MAGIC )
# MAGIC SELECT
# MAGIC     r.`Customer ID`,
# MAGIC     SIZE(COLLECT_SET(`Birthday Date`)),
# MAGIC     SIZE(COLLECT_SET(`First Name`)),
# MAGIC     SIZE(COLLECT_SET(`Last Name`)),
# MAGIC     SIZE(COLLECT_SET(Gender)),
# MAGIC     SIZE(COLLECT_SET(`Marital Status`)),
# MAGIC     SIZE(COLLECT_SET(Email)),
# MAGIC     SIZE(COLLECT_SET(`Phone Number`)),
# MAGIC     SIZE(COLLECT_SET(`Children Amount`)),
# MAGIC     SIZE(COLLECT_SET(City)),
# MAGIC     SIZE(COLLECT_SET(Country)),
# MAGIC     SIZE(COLLECT_SET(`Postal Code`)),
# MAGIC     SIZE(COLLECT_SET(`Preferred Language`)),
# MAGIC     SIZE(COLLECT_SET(`Favorite Brand`)),
# MAGIC     SIZE(COLLECT_SET(`Sign Up Date`)),
# MAGIC     SIZE(COLLECT_SET(`Full Name`))
# MAGIC FROM
# MAGIC     raw_customer_enriched r
# MAGIC JOIN
# MAGIC     natural_key_counts
# MAGIC USING
# MAGIC     (`Customer ID`)
# MAGIC GROUP BY
# MAGIC     r.`Customer ID`
# MAGIC HAVING
# MAGIC     SIZE(COLLECT_SET(`Birthday Date`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`First Name`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Last Name`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(Gender)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Marital Status`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(Email)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Phone Number`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Children Amount`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(City)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(Country)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Postal Code`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Preferred Language`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Favorite Brand`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Sign Up Date`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Full Name`)) > 1

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 07-4 Loading raw_customer_df_enriched DataFrame into silver.raw_customer_enriched table

# CELL ********************

loading_enriched_table(
    df_source=raw_customer_df_enriched,
    target_table="silver.raw_customer_enriched",
    candidate_key=["Customer ID"]
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 08 Data transformation for silver.truck_enriched table

# MARKDOWN ********************

# ### 08-1 Getting data from bronze.truck table

# CELL ********************

truck_df = spark.read.table("bronze.truck")

display(truck_df.limit(10))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# - Handling missing values

# CELL ********************

display(truck_df.select([count(when(col(column).isNull(), column)).alias(column) for column in truck_df.columns]))
print("Total rows: ", truck_df.count())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 08-2 Renaming columns from truck_df DataFrame

# CELL ********************

truck_df_renamed = truck_df.select(
    col("Column1").cast(IntegerType()).alias("Truck ID"),
    col("Column2").cast(IntegerType()).alias("Menu Type ID"),
    col("Column13").cast(IntegerType()).alias("Franchise Owner ID"),
    # Replacing values on manufacturer column
    replace(col("Column10"), lit("Ford_"), lit("Ford")).alias("Manufacturer"),
    col("Column11").alias("Model"),
    col("Column3").alias("City"),
    col("Column5").alias("Region Code (ISO)"),
    col("Column4").alias("Region"),
    col("Column7").alias("Country Code (ISO)"),
    col("Column6").alias("Country"),
    col("Column9").cast(IntegerType()).alias("Opening Year"),
    col("Column8").cast(IntegerType()).alias("Is Franchise Flag"),
    col("Column12").cast(IntegerType()).alias("Is EV Flag"),
    col("Loaded at").cast(TimestampType()).alias("Loaded at (UTC)")
)

display(truck_df_renamed.limit(10))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

truck_df_renamed.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 08-3 Adding calculated columns to truck_df_renamed DataFrame

# CELL ********************

truck_df_enriched = truck_df_renamed.withColumn(
    "Operating Age",
    year(current_date()) - col("Opening Year")
)

display(truck_df_enriched.limit(10))
print("Total rows: ", truck_df_enriched.count())
print("Total distinct rows: ", truck_df_enriched.distinct().count())
print("Total distinct natural key rows: ", truck_df_enriched.select("Truck ID").distinct().count())

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

truck_df_enriched.printSchema()

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# - Handling duplicate values on natural key

# CELL ********************

truck_df_enriched.createOrReplaceTempView("truck_enriched")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC WITH natural_key_counts AS (
# MAGIC     SELECT 
# MAGIC         `Truck ID`, 
# MAGIC         COUNT(*) AS Count
# MAGIC     FROM
# MAGIC         truck_enriched
# MAGIC     GROUP BY
# MAGIC         `Truck ID`
# MAGIC     HAVING
# MAGIC         COUNT(*) > 1
# MAGIC )
# MAGIC SELECT
# MAGIC     t.`Truck ID`,
# MAGIC     SIZE(COLLECT_SET(`Menu Type ID`)),
# MAGIC     SIZE(COLLECT_SET(`Franchise Owner ID`)),
# MAGIC     SIZE(COLLECT_SET(Manufacturer)),
# MAGIC     SIZE(COLLECT_SET(Model)),
# MAGIC     SIZE(COLLECT_SET(City)),
# MAGIC     SIZE(COLLECT_SET(`Region Code (ISO)`)),
# MAGIC     SIZE(COLLECT_SET(Region)),
# MAGIC     SIZE(COLLECT_SET(`Country Code (ISO)`)),
# MAGIC     SIZE(COLLECT_SET(Country)),
# MAGIC     SIZE(COLLECT_SET(`Opening Year`)),
# MAGIC     SIZE(COLLECT_SET(`Is Franchise Flag`)),
# MAGIC     SIZE(COLLECT_SET(`Is EV Flag`)),
# MAGIC     SIZE(COLLECT_SET(`Operating Age`))
# MAGIC FROM
# MAGIC     truck_enriched t
# MAGIC JOIN
# MAGIC     natural_key_counts
# MAGIC USING
# MAGIC     (`Truck ID`)
# MAGIC GROUP BY
# MAGIC     t.`Truck ID`
# MAGIC HAVING
# MAGIC     SIZE(COLLECT_SET(`Menu Type ID`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Franchise Owner ID`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(Manufacturer)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(Model)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(City)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Region Code (ISO)`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(Region)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Country Code (ISO)`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(Country)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Opening Year`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Is Franchise Flag`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Is EV Flag`)) > 1
# MAGIC OR
# MAGIC     SIZE(COLLECT_SET(`Operating Age`)) > 1

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ### 08-4 Loading truck_df_enriched DataFrame into silver.truck_enriched table

# CELL ********************

loading_enriched_table(
    df_source=truck_df_enriched,
    target_table="silver.truck_enriched",
    candidate_key=["Truck ID"]
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
