import numpy as np
import pandas as pd
import streamlit as st
import langchain
import openai
import base64
from io import BytesIO
from datetime import datetime
from google.cloud import bigquery
from google.oauth2 import service_account
from openai_functions import bankruptcy_status
from dataframe_functions import load_df_to_bq

st.markdown("""
<style>
    hr {
        margin-top: 0px;
        margin-bottom: 0px;
        background-color: white; 
    }
    .stFileUploader {
        margin-top: -20px;
        margin-bottom: 0px;
    }
    .stApp {
        background-color: black;
    }
    .stHeader {
        background-color: black;
    }
    section[data-testid="stSidebar"] > div:first-child {
        background-color: #262730;
    }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    cols = st.columns([0.3,2.25,1.7])
    with cols[1]:
        st.image('EY Logo2.PNG')

    cols = st.columns([0.3,4.7])
    with cols[1]:
        st.markdown(f"""<div style="border-radius: 5px;"><h4 style="text-align:left; color: white; font-weight: bold;">Default Identification and SICR Dashboards</h4></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div style="border-radius: 5px;"><h5 style="text-align:left; color: white; ">Follow the below steps:</h5></div>""", unsafe_allow_html=True)

        df = pd.read_excel('template.xlsx')
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='xlsxwriter')
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="template.xlsx">attached</a>'
        
        st.markdown(f"""
        <div style="border-radius: 5px;">
            <h5 style="text-align:left; color: white;">
                <p style="margin-bottom: 5px; font-size: 13px;">1. Prepare the data as per the {href} template</p>
                <p style="margin-bottom: 5px; font-size: 13px;">2. Upload the data file</p>
                <p style="margin-bottom: 5px; font-size: 13px;">3. Visualize the data in the dashboard</p>
            </h5>
        </div>
        """, unsafe_allow_html=True)

st.markdown(f"""<div style="border-radius: 5px;"><h3 style="text-align:left; color: white; font-weight: bold;">Credit Risk Management Standards</h3></div>""", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f"""<div style="border-radius: 5px;"><h5 style="text-align:left; color: white;">Upload data files</h5></div>""", unsafe_allow_html=True)

upload_raw_file = st.file_uploader('', type = 'xlsx')

if upload_raw_file:
    raw_file = pd.read_excel(upload_raw_file).head(15)

    with st.spinner('Checking Bankruptcy Status'):
        raw_file = bankruptcy_status(raw_file)
  
    cols = st.columns([1, 0.7, 0.7])
    with cols[0]:
        st.markdown("""<div style='text-align: left; padding-left: 10px; color: #9cdea8; border-radius: 5px;'><p>Bankruptcy status check completed.</p></div>""", unsafe_allow_html=True)


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
  
    st.markdown("""<div style='text-align: left; padding-left: 10px; color: #9cdea8; border-radius: 5px;'><p>Data has been loaded successfully.</p></div>""", unsafe_allow_html=True)
    

    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"""<div style="border-radius: 5px;"><h5 style="text-align:left; color: white;">Dashboard</h5></div>""", unsafe_allow_html=True)

    st.markdown(
        '<span style="color:white; padding-left: 10px;">The dashboard consists of:</span>'
        '<ul style="padding-left: 10px;">'
        '<li><span style="color:white; padding-left: 10px;">Page 1 - Summary page.</span></li>'
        '<li><span style="color:white; padding-left: 10px;">Page 2 - Detailed page.</span></li>'
        '</ul>',
        unsafe_allow_html=True
    )

    
    
    st.markdown('<span style="color:white; padding-left: 10px;">Click</span> <a href="https://app.powerbi.com/groups/me/reports/5a20d194-6580-44f3-b3ad-859db99fa2cf/9e39d52da42790344bc0?experience=power-bi&bookmarkGuid=3121b084064a018d683b">here</a><span style="color:white;"> to view the dashboard</span>', unsafe_allow_html=True)
