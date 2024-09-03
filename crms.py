import numpy as np
import pandas as pd
import streamlit as st
import langchain
import openai
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account
from openai_functions import bankruptcy_status
from dataframe_functions import load_df_to_bq

st.markdown(f"""<div style="border-radius: 5px;"><h3 style="text-align:left; color: black; font-weight: bold;">Credit Risk Management Standards</h3></div>""", unsafe_allow_html=True)

upload_raw_file = st.file_uploader('Upload Data Files', type = 'xlsx')

if upload_raw_file:
  raw_file = pd.read_excel(upload_raw_file).head(15)

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








dataset_id = 'crms_dataset'
table_id = 'utp_raw'
df = raw_file.sort_values('customer_id')

with st.spinner('Data is being loaded...'):
  load_df_to_bq(df, dataset_id, table_id)

st.markdown("""<div style='text-align: left; padding-left: 10px; color: green; border-radius: 5px;'><p>Data has been loaded successfully.</p></div>""", unsafe_allow_html=True)



