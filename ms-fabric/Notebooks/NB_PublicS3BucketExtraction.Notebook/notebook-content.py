# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "2ca76da9-42d0-4156-bb7e-ec988ef7f874",
# META       "default_lakehouse_name": "LH_FoodTruckNetwork",
# META       "default_lakehouse_workspace_id": "ac2685d9-144e-45ff-afea-351c6539af85",
# META       "known_lakehouses": [
# META         {
# META           "id": "2ca76da9-42d0-4156-bb7e-ec988ef7f874"
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

# # Data Extraction from Public S3 Bucket

# MARKDOWN ********************

# ## 00 Importing packages

# CELL ********************

from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

from botocore.config import Config
from botocore import UNSIGNED
import boto3

from dotenv import load_dotenv
import os

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 01 Getting the key vault secrets

# CELL ********************

# Define service principal and key vault details
load_dotenv("/lakehouse/default/Files/.env")
tenant_id = os.getenv("TENANT_ID")
client_id= os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
vault_uri= os.getenv("VAULT_URI")
secret_name = os.getenv("SECRET_NAME")

# Authenticate key vault client using service principal credential
credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)
keyvault_client = SecretClient(vault_url=vault_uri, credential=credential)

# Retrive the key vault secrets
retrieved_secret = keyvault_client.get_secret(secret_name)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# MARKDOWN ********************

# ## 02 Downloading files from the public S3 bucket

# CELL ********************

# Define s3 and local path
s3_bucket = retrieved_secret.value
s3_folders = [
    "raw_pos",
    "raw_customer"
]
local_folder = "/lakehouse/default/Files/tastybytes"

# Authenticate s3 client without credential
s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))

for folder in s3_folders:
    # Get list of files in the public S3 bucket
    response = s3.list_objects_v2(Bucket=s3_bucket, Prefix=f"frostbyte_tastybytes/{folder}")

    for object in response.get("Contents", []):
        # Get s3 file/folder path 
        key = object["Key"]

        # Skip s3 folder path
        if key.endswith("/"):
            continue

        # Define local file path and create local directory path based on s3 file path
        local_file = os.path.join(local_folder, key.replace('frostbyte_tastybytes/', ''))
        os.makedirs(os.path.dirname(local_file), exist_ok=True)
        
        # Download the s3 file path to local file path
        s3.download_file(s3_bucket, key, local_file)
        print("Successfully downloaded")
        print(f"===> from: {key}")
        print(f"===> to: {local_file}\n")

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
