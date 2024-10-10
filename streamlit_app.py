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
from dataframe_functions import load_df_to_bq
from openai_functions import external_bankruptcy_status

from functions import *

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
    </style>
    """, unsafe_allow_html=True)
 
with st.sidebar:
    cols = st.columns([0.3,2.25,1.7])
    with cols[1]:
        st.image('EY Logo2.PNG')

    cols = st.columns([0.3,4.7])
    with cols[1]:
        st.markdown(f"""<div style="border-radius: 5px;"><h4 style="text-align:left; color: white; font-weight: bold;">Default Identification Dashboard</h4></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div style="border-radius: 5px;"><h5 style="text-align:left; color: white; ">Follow the below steps:</h5></div>""", unsafe_allow_html=True)

        try:
            xls = pd.read_excel('Data Dictionary.xlsx', sheet_name=None)
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
        buffer = BytesIO()
        # df.to_excel(buffer, index=False, engine='xlsxwriter')
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            for sheet_name, df in xls.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="Data Dictionary.xlsx" style="text-decoration: none;">attached</a>'
        
        st.markdown(f"""
        <div style="border-radius: 5px;">
            <h5 style="text-align:left; color: white;">
                <p style="margin-bottom: 5px; font-size: 13px;">1. Prepare the data as per the {href} data dictionary.</p>
                <p style="margin-bottom: 5px; font-size: 13px;">2. Upload the data file.</p>
                <p style="margin-bottom: 5px; font-size: 13px;">3. Visualize the data in the dashboard.</p>
            </h5>
        </div>
        """, unsafe_allow_html=True)

st.markdown(f"""<div style="border-radius: 5px;"><h3 style="text-align:left; color: white; font-weight: bold;">Credit Risk Management Standards</h3></div>""", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(f"""<div style="border-radius: 5px;"><h5 style="text-align:left; color: white;">Upload data files</h5></div>""", unsafe_allow_html=True)

upload_raw_file = st.file_uploader('', type = 'xlsx')

if upload_raw_file:

    with st.spinner('Data is being processed...'):
        # raw_file = pd.read_excel(upload_raw_file).head(5)
        df = pd.read_excel(upload_raw_file, sheet_name = 'Raw')
        df_assumptions = pd.read_excel(upload_raw_file, sheet_name = 'Assumptions')
        df_collateral = pd.read_excel(upload_raw_file, sheet_name = 'Collateral')
        df_pre_restructure = pd.read_excel(upload_raw_file, sheet_name = 'Pre-Restructures')
        df_income_source = pd.read_excel(upload_raw_file, sheet_name = 'Income Source')
        df_login_history = pd.read_excel(upload_raw_file, sheet_name = 'User Login History')
        df_cb_defaults = pd.read_excel(upload_raw_file, sheet_name = 'CBUAE defaults list')
    
        st.session_state.discount_rate = df_assumptions['Discount Rate'].iloc[0]
        default_rating = list(df_assumptions['Default Internal Ratings'])
    
        # df = dpd_90_plus_flag(df)
        df = specific_provision_held(df)
        df = non_accrued_status(df)
        df = covenant_breach_flag(df)
        df = loss_of_key_staff(df)
        df = bank_flag(df)
        df = dbr_flag(df)
        df = litigation_flag(df)
        df = breach_major_terms_OR_non_payments(df)
        df = capable_but_unwilling_flag(df, default_rating)
        df = likelihood_of_bankruptcy(df, default_rating)
        df = economic_loss_flag(df, df_assumptions)
        df = collateral_liquidation_flag(df, df_collateral)
        df = material_concession_flag(df, df_assumptions, df_pre_restructure)
        df = financial_deterioration_flag(df, df_assumptions)
        df = operating_assets_degradation_flag(df)
        df = collateral_degradation_flag(df)
        df = material_overdraft_flag(df)
        df = income_degradation_flag(df, df_income_source)
        df = obligor_not_in_uae_6m(df, df_login_history)
        df = obligor_not_in_uae_3m(df, df_login_history)
        df = repeated_restructuring_flag(df, df_assumptions)
        df = cbuae_defaulted(df, df_cb_defaults)
    
        
        # wholesale_custs = list(set(df[df['Wholesale Flag'] == 1]['Customer Name']))
        # cust_ext_flag = pd.DataFrame({'Customer Name' : wholesale_custs})
        # st.write(cust_ext_flag)
        # cust_ext_flag['External Bankruptcy Flag'] = cust_ext_flag['Customer Name'].apply(external_bankruptcy_status)
    
        # df = df.merge(cust_ext_flag, how = 'left', on = 'Customer Name')
        # df.loc[df['External Bankruptcy Flag'].isna(), 'External Bankruptcy Flag'] = 0
    
        df["External Bankruptcy Flag"] = 0
        df["Obligor classified default by rating agency"] = 0
        df["Crisis in the obligor's sector"] = 0
        df["Subsidiary default with obligor guarantee"] = 0
        # df["Breach of major terms or non-payment"] = 0


        
        df["Bank filed obligor's bankruptcy order"] = 0
        df.loc[(df['External Bankruptcy Flag'] == 1) | (df['Internal Bankruptcy Flag'] == 1), "Bank filed obligor's bankruptcy order"] = 1
        
        # df = external_bankruptcy_status(df)
        
        # # st.write(cust_ext_flag, df)
        
        # st.write(df)
    
        max_date = max(df['As of Date'])
    
        df = df[df['As of Date'] == max_date].reset_index(drop = True)
    
        flag_cols = [
                    "Account-specific provision held",
                    "Credit facility on a non-accrued status",
                    "Partial facility sale at economic loss",
                    "Bank filed obligor's bankruptcy order",
                    "Obligor's default by another FI",
                    "Obligor's unwillingness to meet obligations",
                    "Liquidation of collateral due to decline in the obligor's credit worthiness",
                    "Obligor classified default by rating agency",
                    "Material concessions granted under restructuring terms",
                    "Obligor's income sources no longer exist or distressed",
                    "A significant deterioration in the value of collateral",

                    "Obligor's owner left UAE without clear rationale for 6 plus months",
                    "Significant deterioration in financial performance",
                    "High likelihood of bankruptcy or financial reorganization",
                    "Breach of material covenant in Credit facility",
                    "Repeated restructurings due to financial difficulties",
                    "Significant deterioration in operating assets",
                    "Pending litigation or  regulatory changes with negative impact",
                    "A loss of key staff to obligor's organization",
                    "Material overdraft consistently at or above limits with irregular inflows",
                    "External circumstances affecting repayment ability",
                    "Crisis in the obligor's sector",
                    "Subsidiary default with obligor guarantee",
                    "Breach of major terms or non-payment",
            
                    "Obligor's owner left UAE without clear rationale for 3 plus months",
                    "Stressed DBR breaches internal limits"]
    
    
        df_final = df[flag_cols]
        df_final['default_trigger'] = df[flag_cols].any(axis=1).astype(int)
        df_final['customer_id'] = df['Customer ID']
        df_final['facility_id'] = df['Facility ID']
        df_final['customer_name'] = df['Customer Name']
        df_final['facility_id'] = df['Facility ID']
        df_final['added_at'] = datetime.now()
        df_final['asset_type'] = df['Asset Type']
        df_final['line_of_business'] = df['Line of Business']
        df_final['whole_sale_flag'] = df['Wholesale Flag']
        df_final['exposure_amount'] = df['Exposure (AED)']
    
        non_flag_cols = ['added_at', 'customer_id', 'facility_id', 'whole_sale_flag', 'customer_name', 'exposure_amount', 'asset_type', 'line_of_business', 'default_trigger']
        
        df_final = df_final[non_flag_cols + flag_cols]
        
        # st.write(df_final)
    
        # df_final_retail = df_final.loc[df_final['whole_sale_flag'] == 0].reset_index(drop = True)
    
    
    
    
    
    
        # TRANSFORMED FILE #
        trigger_cols = df_final.columns[9:]
        final_df = pd.DataFrame(columns = ['customer_id', 'facility_id', 'whole_sale_flag', 'customer_name', 'asset_type', 'line_of_business', 'exposure_amount', 'trigger', 'flag', 'default_trigger'])
      
        for i in range(0, len(df_final)):
            for j in trigger_cols:
                temp_df_list = [df_final['customer_id'][i], df_final['facility_id'][i], df_final['whole_sale_flag'][i], df_final['customer_name'][i], df_final['asset_type'][i], df_final['line_of_business'][i], df_final['exposure_amount'][i], j, df_final[j][i], df_final['default_trigger'][i]]
                temp_df = pd.DataFrame(temp_df_list).T
                temp_df.columns = final_df.columns
                
                final_df = pd.concat([final_df, temp_df]).reset_index(drop = True)
    
        final_df['cust_def_flag'] = 'No'
        final_df.loc[final_df['default_trigger'] == 1, 'cust_def_flag'] = 'Yes'
        final_df.insert(0, 'added_at', datetime.now())
    
        # st.write(final_df)
    
        final_df_retail = final_df.loc[final_df['whole_sale_flag'] == 0].reset_index(drop = True)

        non_retail_flags = ["Obligor's owner left UAE without clear rationale for 6 plus months",
                            "Significant deterioration in financial performance",
                            "High likelihood of bankruptcy or financial reorganization",
                            "Breach of material covenant in Credit facility",
                            "Repeated restructurings due to financial difficulties",
                            "Significant deterioration in operating assets",
                            "Pending litigation or  regulatory changes with negative impact",
                            "A loss of key staff to obligor's organization",
                            "Material overdraft consistently at or above limits with irregular inflows",
                            "External circumstances affecting repayment ability",
                            "Crisis in the obligor's sector",
                            "Subsidiary default with obligor guarantee",
                            "Breach of major terms or non-payment"]

        final_df_retail = final_df_retail[~final_df_retail['trigger'].isin(non_retail_flags)].reset_index(drop = True)
        # final_df_retail['rm_comments'] = ''













        
    
    
        final_df_wholesale = final_df.loc[final_df['whole_sale_flag'] == 1].reset_index(drop = True)
        final_df_wholesale = final_df_wholesale.groupby(['added_at', 'facility_id', 'customer_id', 'whole_sale_flag', 'customer_name', 'asset_type',
                                                         'line_of_business', 'trigger']).agg(exposure_amount = ('exposure_amount', 'sum'),
                                                                                             flag = ('flag', 'max'),
                                                                                             default_trigger = ('default_trigger', 'max')).reset_index()
        
        final_df_wholesale['cust_def_flag'] = 'No'
        final_df_wholesale.loc[final_df_wholesale['default_trigger'] == 1, 'cust_def_flag'] = 'Yes'


        non_wholesale_flags = ["Obligor's owner left UAE without clear rationale for 3 plus months",
                                "Stressed DBR breaches internal limits"]

        final_df_wholesale = final_df_wholesale[~final_df_wholesale['trigger'].isin(non_wholesale_flags)].reset_index(drop = True)
        # final_df_wholesale['rm_comments'] = ''

        
    
    
        st.markdown("""<div style='text-align: left; padding-left: 10px; color: #9cdea8; border-radius: 5px;'><p>Data has been processed successfully.</p></div>""", unsafe_allow_html=True)
        


    # grouped_wholesale = final_df_wholesale[['customer_id', 'facility_id',
    #                     'default_trigger']].groupby(['customer_id', 'facility_id']).agg(Obligor_cross_default = ('default_trigger','max')).reset_index()
    # df_final = df_final.merge(grouped_wholesale, how = 'left', on = ['customer_id', 'facility_id']).reset_index(drop = True)

    # obligor_column = df_final.pop('Obligor_cross_default')
    # line_of_business_index = df_final.columns.get_loc('line_of_business')
    # df_final.insert(line_of_business_index + 1, 'Obligor_cross_default', obligor_column)

    # df_final.loc[df_final['Obligor_cross_default'].isna(), 'Obligor_cross_default'] = df_final['default_trigger']
    
    # st.write(df_final)

    df_final.rename(columns = {"default_trigger":"utp_trigger"}, inplace = True)

    df_final['latest'] = 1
    final_df_retail['latest'] = 1
    final_df_wholesale['latest'] = 1


    with st.spinner('Data is being loaded...'):
        load_df_to_bq(df_final.sort_values('customer_id'), 'crms_dataset', 'utp_raw')
        load_df_to_bq(final_df_retail, 'crms_dataset', 'utp_transformed')
        load_df_to_bq(final_df_wholesale, 'crms_dataset', 'utp_transformed_wholesale')
        
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

    st.markdown('<span style="color:white; padding-left: 10px;">Click</span> <a href="https://apps.powerapps.com/play/e/a3c669f6-ac2e-4e77-ad43-beab3e15bee7/a/59a11872-a620-40b2-b23a-7aa4f7906d7e?tenantId=5b973f99-77df-4beb-b27d-aa0c70b8482c&hint=f693551a-ac73-4be1-931b-a270f8c88c90&sourcetime=1725760991210" style="text-decoration: none;">here</a><span style="color:white;"> to view the dashboard.</span>', unsafe_allow_html=True)

    buffer = BytesIO()
    df_final.to_excel(buffer, index=False, engine='xlsxwriter')
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Raw Data.xlsx" style="text-decoration: none;">here</a>'
    
    st.markdown(f"""
    <span style="color: white; padding-left: 10px; margin-top: -20px;">
            Click {href} to download raw data.</p>
            
    </span>
    """, unsafe_allow_html=True)
