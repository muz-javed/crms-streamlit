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
  raw_file = pd.read_excel(upload_raw_file).head(11)

  with st.spinner('Checking Bankruptcy Status'):
    raw_file = bankruptcy_status(raw_file)
  
    cols = st.columns([1, 0.7, 0.7])
    with cols[0]:
      st.markdown("""<div style='text-align: left; padding-left: 10px; color: green; border-radius: 5px;'><p>Bankruptcy status check completed.</p></div>""", unsafe_allow_html=True)


  ### CONVERT TO THE POWER-BI FORMAT ###
  raw_file.insert(0, 'added_at', datetime.now())

  # raw_file['default_trigger'] = 0
  # raw_file.loc[raw_file['']]

  st.write(raw_file[raw_file.columns[6:]].sum(axis = 1))

  st.write(raw_file)

