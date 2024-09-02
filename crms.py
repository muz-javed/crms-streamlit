import numpy as np
import pandas as pd
import streamlit as st
import langchain
import openai
from datetime import datetime
# from openai_functions import bankruptcy_status

st.markdown(f"""<div style="border-radius: 5px;"><h3 style="text-align:left; color: black; font-weight: bold;">Credit Risk Management Standards</h3></div>""", unsafe_allow_html=True)

upload_raw_file = st.file_uploader('Upload Data Files', type = 'xlsx')

if upload_raw_file:
  raw_file = pd.read_excel(upload_raw_file).head(1)








  

  # with st.spinner('Checking Bankruptcy Status'):
  #   raw_file = bankruptcy_status(raw_file)
  
  #   cols = st.columns([1, 0.7, 0.7])
  #   with cols[0]:
  #     st.markdown("""<div style='text-align: left; padding-left: 10px; color: green; border-radius: 5px;'><p>Bankruptcy status check completed.</p></div>""", unsafe_allow_html=True)


  # ### CONVERT TO THE POWER-BI FORMAT ###
  # raw_file.insert(0, 'added_at', datetime.now())

  # # raw_file['default_trigger'] = 0
  # # raw_file.loc[raw_file['']]

  st.write(raw_file.columns[6:])

  st.write(raw_file)



GOOGLE_API_KEY = "AIzaSyBjWM0cyxXBjoiRgdh7cFbSJImF6U05HpU"
GOOGLE_CSE_ID = "d6a7169ef0a274385"

import os
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")


import requests

# Replace these with your actual API key and CSE ID
query = 'Python programming'  # Replace with your search query

# Construct the URL for the API request
url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={query}"

# Send the GET request to the API
response = requests.get(url)

# Parse the JSON response
results = response.json()

# Check if the request was successful
if 'items' in results:
    for i, item in enumerate(results['items'], start=1):
        st.write(f"Result {i}:")
        st.write(f"Title: {item['title']}")
        st.write(f"Link: {item['link']}\n")
else:
    st.write("No results found or there was an error with the request.")






