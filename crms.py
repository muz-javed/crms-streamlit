import numpy as np
import pandas as pd
import streamlit as st
import langchain
import openai

from openai_functions import bankruptcy_status

st.markdown(f"""<div style="border-radius: 5px;"><h3 style="text-align:left; color: black; font-weight: bold;">Credit Risk Management Standards</h3></div>""", unsafe_allow_html=True)

upload_raw_file = st.file_uploader('Upload Data Files', type = 'xlsx')

if upload_raw_file:
  raw_file = pd.read_excel(upload_raw_file).head(5)

  st.write(raw_file)




