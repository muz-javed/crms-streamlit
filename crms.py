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
  # UTP - RAW file #
  raw_file.insert(0, 'added_at', datetime.now())

  raw_file['default_trigger'] = raw_file[raw_file.columns[6:]].sum(axis = 1)
  raw_file.loc[raw_file['default_trigger'] > 1, 'default_trigger'] = 1

  cols = raw_file.columns.tolist()
  line_of_business_index = cols.index('line_of_business')
  cols.insert(line_of_business_index + 1, cols.pop(cols.index("default_trigger")))
  raw_file = raw_file[cols]

  # TRANSFORMED FILE #
  trigger_cols = raw_file.columns[7:]
  final_df = pd.DataFrame(columns = ['customer_id', 'customer_name', 'asset_type', 'line_of_business', 'exposure_amount', 'trigger', 'flag', 'default_trigger'])
  
  for i in range(0, len(raw_file)):
    for j in trigger_cols:
  
      temp_df_list = [raw_file['customer_id'][i], raw_file['customer_name'][i], raw_file['asset_type'][i], raw_file['line_of_business'][i], raw_file['exposure_amount'][i], j, raw_file[j][i], raw_file['default_trigger'][i]]
      temp_df = pd.DataFrame(temp_df_list).T
      temp_df.columns = final_df.columns

      final_df = pd.concat([final_df, temp_df]).reset_index(drop = True)
  
  final_df['cust_def_flag'] = 'No'
  final_df.loc[final_df['default_trigger'] == 1, 'cust_def_flag'] = 'Yes'
  final_df.insert(0, 'added_at', datetime.now())
  
  with st.spinner('Data is being loaded...'):
    load_df_to_bq(raw_file.sort_values('customer_id'), 'crms_dataset', 'utp_raw')
    load_df_to_bq(final_df, 'crms_dataset', 'utp_transformed')
  
  st.markdown("""<div style='text-align: left; padding-left: 10px; color: green; border-radius: 5px;'><p>Data has been loaded successfully.</p></div>""", unsafe_allow_html=True)



