import numpy as np
import pandas as pd
import streamlit as st

# 90 Plus DPD Flag
def dpd_90_plus_flag(df):
    temp_custs = df.groupby(['As of Date', 'Customer ID']).agg(total_exp = ('Exposure (AED)', 'sum'))
    df = df.merge(temp_custs, how = 'left', on = ['As of Date', 'Customer ID']).reset_index(drop = True)
    df['materiality_perc'] = df['Exposure (AED)']/df['total_exp']

    df['90+ DPD'] = 0
    df.loc[(df['materiality_perc'] > 0.05) & (df['DPD'] > 90), '90+ DPD'] = 1

    return df

# Account Specific Provisions
def specific_provision_held(df):
    df['Account-specific provision held'] = 0
    df.loc[df['Stage'] == 'Stage 3', 'Account-specific provision held'] = 1
    
    return df

# Non-Accrued Status
def non_accrued_status(df):
    df['Credit facility on a non-accrued status'] = 0
    df.loc[df['Interest Accrual Status'] == 1, 'Credit facility on a non-accrued status'] = 1

    return df

# DBR Flag
def dbr_flag(df):
    df['DBR Flag'] = 0
    df.loc[(df['DBR Flag'] == 1) & (df['Wholesale Flag'] == 1), 'DBR Flag'] = 1

    return df

# Litigation
def litigation_flag(df):
    df['Pending litigation or  regulatory changes with negative impact'] = 0
    df.loc[(df['Litigation flag'] == 1) & (df['Wholesale Flag'] == 1), 'Pending litigation or  regulatory changes with negative impact'] = 1

    return df

# Loss of key staff flag
def loss_of_key_staff(df):
    df['A loss of key staff to the obligor’s organization'] = 0
    df.loc[df['Key staff loss flag'] == 1, 'A loss of key staff to the obligor’s organization'] = 1

    return df

# Capable but unwilling to pay
def capable_but_unwilling_flag(df, default_rating):
    df["Obligor's unwillingness to meet obligations"] = 0
    df.loc[(~df['Internal Rating'].isin(default_rating)) & (df['Unwillingness to Pay Flag']) == 1, "Obligor's unwillingness to meet obligations"] = 1

    return df

# Likelihood of bankruptcy
def likelihood_of_bankruptcy(df, default_rating):
    df['A high likelihood that the obligor will enter bankruptcy or other material financial reorganization'] = 0
    df.loc[(df['Internal Rating'].isin(default_rating)), 'A high likelihood that the obligor will enter bankruptcy or other material financial reorganization'] = 1

    return df

# Get NPV Value
def get_npv_value(df, df_assumptions):
    
    if df_assumptions['Repayment Type'].iloc[0] == 'Straight Line':
        df = straight_line(df)
    else:
        df = bullet_payments(df)

    return df
    
# Get NPV Value - Bullet
def bullet_payments(df):

    df['years_to_maturity'] = ((df['Facility End Date'] - df['As of Date']).dt.days)/365
    df['NPV'] = df['Exposure (AED)']/((1 + st.session_state.discount_rate) ** df['years_to_maturity'])

    return df

# Get NPV Value - Straight Line
def straight_line(df):
    
    df['NPV'] = df.apply(straight_line_calcs, axis = 1)

    return df

def straight_line_calcs(row):

    payments = pd.DataFrame({'Date': [row['Facility End Date']]})
    maturity_date = row['Facility End Date']

    while 1:
        payment_date = maturity_date - pd.DateOffset(days=90)
        

        if payment_date < row['As of Date']:
            break

        else:
            maturity_date = payment_date
            temp_payments = pd.DataFrame({'Date': [payment_date]})

            payments = pd.concat([payments, temp_payments]). reset_index(drop = True)

    payments['As of Date'] = row['As of Date']
    payments['Exposure (AED)'] = row['Exposure (AED)']/len(payments)

    payments['years_to_maturity'] = ((payments['Date'] - payments['As of Date']).dt.days)/365
    payments['NPV'] = payments['Exposure (AED)']/((1 + st.session_state.discount_rate) ** payments['years_to_maturity'])
    
    npv = payments['NPV'].sum()

    return npv


# Economic Loss Flag
def economic_loss_flag(df, df_assumptions):

    df = get_npv_value(df, df_assumptions)
    df['sale_price_loss'] = 1 - (df['Sale Price of Facility (if applicable)']/df[['Exposure (AED)', 'NPV']].max(axis = 1))
    df['Partial facility sale at economic loss'] = 0
    df.loc[(~df['Sale Price of Facility (if applicable)'].isna()) & (df['sale_price_loss'] > 0.3), 'Partial facility sale at economic loss'] = 1

    return df


# Collateral Liquidation Flag
def collateral_liquidation_flag(df, df_collateral):
    dates_df = pd.DataFrame(set(df_collateral['As of Date']))
    
    dates_df.columns = ['As of Date']
    dates_df['Rank'] = dates_df['As of Date'].rank(ascending=False, method='min')
    
    df_collateral = df_collateral.merge(dates_df, how = 'left', on = 'As of Date')
    
    df["Liquidation of collateral due to decline in the obligor’s credit worthiness"] = 0
    as_of_date = df_collateral[df_collateral['Rank'] == 1]['As of Date'].iloc[0]
    
    for f_id in set(df_collateral[df_collateral['Rank'] == 1]['Facility ID']):
    
        rank_1 = list(df_collateral[(df_collateral['Facility ID'] == f_id) & (df_collateral['Rank'] == 1)]['Collateral ID'])
        rank_2 = list(df_collateral[(df_collateral['Facility ID'] == f_id) & (df_collateral['Rank'] == 2)]['Collateral ID'])
    
        if len(list(set(rank_2) - set(rank_1))) > 0:
            df.loc[(df['Facility ID'] == f_id) & (df['As of Date'] == as_of_date), "Liquidation of collateral due to decline in the obligor’s credit worthiness"] = 1

    return df


# Material Concession Flag
def material_concession_flag(df, df_assumptions):
    df = get_npv_value(df, df_assumptions)
    max_date = max(df['As of Date'])
    
    df_temp_restructues = get_npv_value(df_pre_restructure, df_assumptions)
    df_temp_restructues.rename(columns = {'NPV':'NPV Pre-Restructures'}, inplace = True)
    
    df_temp_restructues = df_temp_restructues.merge(df[df['As of Date'] == max_date][['Facility ID', 'NPV']].reset_index(drop = True), how = 'left', on = 'Facility ID').reset_index(drop = True)
    
    df_temp_restructues['material_concession_perc'] = (df_temp_restructues['NPV Pre-Restructures'] - df_temp_restructues['NPV'])/df_temp_restructues['NPV Pre-Restructures']
    
    df_temp_restructues['Material concessions granted under restructuring terms'] = 0
    df_temp_restructues.loc[df_temp_restructues['material_concession_perc'] > 0.01, 'Material concessions granted under restructuring terms'] = 1
    
    df = df.merge(df_temp_restructues[['As of Date', 'Facility ID', 'NPV Pre-Restructures', 'material_concession_perc', 'Material concessions granted under restructuring terms']],
                  how = 'left', on = ['As of Date', 'Facility ID']).reset_index(drop = True)
    
    df.loc[df['Material concessions granted under restructuring terms'].isna(), 'Material concessions granted under restructuring terms'] = 0

    return df


# Financial deterioration flag
def financial_deterioration_flag(df, df_assumptions):
    current_ratio = df_assumptions['Current Ratio Threshold'].iloc[0]
    quick_ratio = df_assumptions['Quick Ratio Threshold'].iloc[0]
    leverage_ratio = df_assumptions['Leverage Ratio Threshold'].iloc[0]
    
    df['Significant deterioration in financial performance'] = 0
    df.loc[((df['Current Ratio'] < current_ratio) | (df['Quick Ratio'] < quick_ratio) | (df['Leverage Ratio'] > leverage_ratio)) & (df['Wholesale Flag'] == 1), 'Significant deterioration in financial performance'] = 1

    return df


# Collateral Degradation FLag
def collateral_degradation_flag(df):

    df['LTV'] = df['Exposure (AED)']/df['Collateral (AED)']

    df['A significant deterioration in the value of collateral.'] = 0
    df.loc[df['LTV'] > 1, 'A significant deterioration in the value of collateral.'] = 1

    return df


# Material Overdraft FLag
def material_overdraft_flag(df):

    df['material_overdraft_val'] = df['Exposure (AED)']/df['Facility Limit']

    df['Material overdraft consistently at/above limits with irregular inflows'] = 0
    df.loc[df['material_overdraft_val'] > 1.05, 'Material overdraft consistently at/above limits with irregular inflows'] = 1

    return df


# Income Degradation Flag
def income_degradation_flag(df, df_income_source):
    
    current_date = max(df_income_source['As of Date'])
    two_years_back_date = current_date - pd.DateOffset(days=2*365)
    
    two_yrs_df = df_income_source[df_income_source['As of Date'] >= two_years_back_date].reset_index(drop = True)
    two_yrs_df_grouped = two_yrs_df.groupby('Customer ID').agg(avg_funds = ('Funds', 'mean'),
                                                               var_funds = ('Funds', 'var')).reset_index()
    
    current_date_df = df_income_source[df_income_source['As of Date'] == current_date].reset_index(drop = True)
    
    current_date_df = current_date_df.merge(two_yrs_df_grouped, how = 'left', on = 'Customer ID')
    
    current_date_df['std_dev'] = current_date_df['var_funds'].pow(0.5)
    current_date_df['lower_bound'] =current_date_df['avg_funds'] - (0.5 * current_date_df['std_dev'])
    
    current_date_df["Obligor’s income sources no longer exist or distressed"] = 0
    current_date_df.loc[current_date_df['Funds'] < current_date_df['lower_bound'], "Obligor’s income sources no longer exist or distressed"] = 1
    
    df = df.merge(current_date_df[['As of Date', 'Customer ID', "Obligor’s income sources no longer exist or distressed"]], how = 'left', on = ['As of Date', 'Customer ID'])

    df.loc[df["Obligor’s income sources no longer exist or distressed"].isna(), "Obligor’s income sources no longer exist or distressed"] = 0

    return df



# Obligor not in UAE for 6M or more
def obligor_not_in_uae_6m(df, df_login_history):
    current_date = max(df_login_history['Date'])
    six_m_back_date = current_date - pd.DateOffset(days=180)
    
    six_m_df = df_login_history[df_login_history['Date'] >= six_m_back_date].reset_index(drop = True)
    six_m_df["Obligor’s owner left UAE without clear rationale, 6+ months"] = six_m_df['Login Location'].apply(lambda x: 1 if x == 'Outside UAE' else 0)
    six_m_df = six_m_df.groupby('Customer ID').agg({"Obligor’s owner left UAE without clear rationale, 6+ months": 'max'}).reset_index()
    six_m_df['As of Date'] = current_date
    
    df = df.merge(six_m_df, how = 'left', on = ['As of Date', 'Customer ID'])
    df.loc[(df["Obligor’s owner left UAE without clear rationale, 6+ months"].isna()) | (df['Wholesale Flag'] == 0), "Obligor’s owner left UAE without clear rationale, 6+ months"] = 0

    return df


# Obligor not in UAE for 3M or more
def obligor_not_in_uae_3m(df, df_login_history):
    current_date = max(df_login_history['Date'])
    three_m_back_date = current_date - pd.DateOffset(days=90)
    
    three_m_back_date = df_login_history[df_login_history['Date'] >= six_m_back_date].reset_index(drop = True)
    three_m_back_date["Obligor’s owner left UAE without clear rationale, 3+ months"] = three_m_back_date['Login Location'].apply(lambda x: 1 if x == 'Outside UAE' else 0)
    three_m_back_date = three_m_back_date.groupby('Customer ID').agg({"Obligor’s owner left UAE without clear rationale, 3+ months": 'max'}).reset_index()
    three_m_back_date['As of Date'] = current_date
    
    df = df.merge(three_m_back_date, how = 'left', on = ['As of Date', 'Customer ID'])
    df.loc[(df["Obligor’s owner left UAE without clear rationale, 3+ months"].isna()) | (df['Wholesale Flag'] == 1), "Obligor’s owner left UAE without clear rationale, 3+ months"] = 0

    return df

# Repeated Restructured Flag
def repeated_restructuring_flag(df, df_assumptions):
    restructured_flag_threshold = df_assumptions['No of Restructure Threshold (24 M)'].iloc[0]
    
    current_date = max(df['As of Date'])
    two_years_back_date = current_date - pd.DateOffset(days=2*365)
    
    temp_df = df.loc[df['As of Date'] >= two_years_back_date].reset_index(drop = True)
    
    temp_df = temp_df.groupby(['As of Date', 'Customer ID']).agg(res_flag = ('Restructure Flag', 'max')).reset_index()
    
    temp_df = temp_df.groupby('Customer ID').agg(as_of_date = ('As of Date', 'max'), sum_res_flag = ('res_flag', 'sum')).reset_index()
    temp_df.rename(columns = {'as_of_date':'As of Date'}, inplace = True)
    
    temp_df['Repeated restructurings due to financial difficulties'] = 0
    temp_df.loc[temp_df['sum_res_flag'] > restructured_flag_threshold, 'Repeated restructurings due to financial difficulties'] = 1
    
    df = df.merge(temp_df[['Customer ID', 'As of Date', 'Repeated restructurings due to financial difficulties']], how = 'left', on = ['As of Date', 'Customer ID'])
    df.loc[(df['Repeated restructurings due to financial difficulties'].isna()) | (df['Wholesale Flag'] == 0), 'Repeated restructurings due to financial difficulties'] = 0
    
    return df























