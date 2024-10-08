import numpy as np
import pandas as pd
import streamlit as st
import langchain
import openai
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account
from openai_functions import external_bankruptcy_status

def load_df_to_bq(df, dataset_id, table_id):
  # Path to your service account key file (JSON format)
  key_path = "gen-lang-client-0773467639-eb3bb34e9803.json"
  
  # Credentials from the service account key file
  credentials = service_account.Credentials.from_service_account_file(key_path)
  
  # Initialize the BigQuery client with the credentials
  client = bigquery.Client(credentials=credentials, project=credentials.project_id)
  
  # Define your dataset and table name
  table_full_id = f"{client.project}.{dataset_id}.{table_id}"

  # --------------------
  # Step 1: Update 'latest' column in the existing table to 0
  # --------------------
  # Define the SQL query to update 'latest' column to 0

  max_date = df['added_at'].max()
  
  update_query = f"""UPDATE `{table_full_id}` SET latest = 0 WHERE added_at != '{max_date}'"""
  # Execute the query
  query_job = client.query(update_query)
  query_job.result()

  # --------------------
  # Step 2: Append new data from df into the table
  # --------------------
  # Define the job configuration with schema autodetection
  job_config = bigquery.LoadJobConfig(
      autodetect=True,
      write_disposition=bigquery.WriteDisposition.WRITE_APPEND #WRITE_TRUNCATE  # This overwrites the table if it already exists
  )
  # Load the DataFrame into the BigQuery table
  load_job = client.load_table_from_dataframe(df, table_full_id, job_config=job_config)  # Make an API request.
  load_job.result()  # Wait for the job to complete.
    
    
