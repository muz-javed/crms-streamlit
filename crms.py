import numpy as np
import pandas as pd
import streamlit as st
import langchain
import openai
from datetime import datetime
from openai_functions import bankruptcy_status

st.markdown(f"""<div style="border-radius: 5px;"><h3 style="text-align:left; color: black; font-weight: bold;">Credit Risk Management Standards</h3></div>""", unsafe_allow_html=True)

upload_raw_file = st.file_uploader('Upload Data Files', type = 'xlsx')

if upload_raw_file:
  raw_file = pd.read_excel(upload_raw_file).head(5)

  with st.spinner('Checking Bankruptcy Status'):
    raw_file = bankruptcy_status(raw_file)
  
    cols = st.columns([1, 0.7, 0.7])
    with cols[0]:
      st.markdown("""<div style='text-align: left; padding-left: 10px; color: green; border-radius: 5px;'><p>Bankruptcy status check completed.</p></div>""", unsafe_allow_html=True)


  ### CONVERT TO THE POWER-BI FORMAT ###
  raw_file.insert(0, 'added_at', datetime.now())

  raw_file['default_trigger'] = raw_file[raw_file.columns[6:]].sum(axis = 1)
  raw_file.loc[raw_file['default_trigger'] > 1, 'default_trigger'] = 1

  cols = raw_file.columns.tolist()
  line_of_business_index = cols.index('line_of_business')
  cols.insert(line_of_business_index + 1, cols.pop(cols.index("default_trigger")))
  raw_file = raw_file[cols]

  st.write(raw_file)






  from google.cloud import bigquery
  from google.oauth2 import service_account
  import pandas as pd
  
  # Path to your service account key file (JSON format)
  key_path = "gen-lang-client-0773467639-eb3bb34e9803.json"
  
  # Credentials from the service account key file
  credentials = service_account.Credentials.from_service_account_file(key_path)
  
  # Initialize the BigQuery client with the credentials
  client = bigquery.Client(credentials=credentials, project=credentials.project_id)
  
  # Define your dataset and table name
  dataset_id = 'crms_dataset'
  table_id = 'utp_raw'
  table_full_id = f"{client.project}.{dataset_id}.{table_id}"
  
  # Define the job configuration with schema autodetection
  job_config = bigquery.LoadJobConfig(
      autodetect=True,
      write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE  # This overwrites the table if it already exists
  )
  
  # Load the DataFrame into the BigQuery table
  load_job = client.load_table_from_dataframe(raw_file, table_full_id, job_config=job_config)  # Make an API request.
  
  load_job.result()  # Wait for the job to complete.
  
  st.write(f"Loaded {load_job.output_rows} rows into {table_full_id}.")



