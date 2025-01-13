import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Fund Price Comparison", page_icon=":chart_with_upwards_trend:", layout="wide")
# Load data files

import os

# สร้างเส้นทางไฟล์แบบสมบูรณ์
def join_path(relative_path):
    # สร้าง path แบบสมบูรณ์
    base_dir = os.path.dirname(__file__)  # โฟลเดอร์ที่โค้ดนี้อยู่
    return os.path.join(base_dir+"/..", relative_path)

def load_data():
    fund_profiles = pd.read_csv(join_path('data/all_active_funds_TH_overview.csv'))
    fund_nav = pd.read_csv(join_path('data/fund_NAV_history.csv'))
    available_amc = pd.read_csv(join_path('data/avaliable_amc.csv'))
    primary_type = pd.read_csv(join_path('data/sec_code_primary.csv'))
    return fund_profiles, fund_nav, available_amc, primary_type

#st.write(join_path('data/all_active_funds_TH_overview.csv'))
# Prepare NAV data
def prepare_nav_data(fund_nav):
    fund_nav.rename(columns={fund_nav.columns[0]: "Date"}, inplace=True)
    fund_nav['Date'] = pd.to_datetime(fund_nav['Date'])
    return fund_nav.melt(id_vars="Date", var_name="Fund Name", value_name="NAV")

# Sidebar filters
def create_sidebar(fund_profiles, available_amc, primary_type):
    st.sidebar.header("Filters")

    classification_options = fund_profiles['Classification Sector Scheme'].dropna().unique()
    selected_classifications = st.sidebar.multiselect("Classification Sector Scheme:", classification_options)


    fund_type_options = fund_profiles['Fund Type'].dropna().unique()
    selected_fund_types = st.sidebar.multiselect("Fund Type:", fund_type_options)

    amc_filter = st.sidebar.selectbox("Fund Company Filter:", ["All Funds", "Only Tradable Companies"])
    primary_type_filter = st.sidebar.selectbox("Primary Type Filter:", ["All Types", "Only Primary Types"])

    period_options = {
        "1 Month": timedelta(days=30),
        "3 Months": timedelta(days=90),
        "6 Months": timedelta(days=180),
        "1 Year": timedelta(days=365),
        "3 Years": timedelta(days=1095),
        "5 Years": timedelta(days=1825)
    }
    selected_period = st.sidebar.selectbox("Select Period:", list(period_options.keys()))

    num_funds = st.sidebar.number_input("Number of Funds to Display:", min_value=1, value=5, step=1)
    display_type = st.sidebar.selectbox("Display Type:", ["Top Performers", "Bottom Performers"])

    return (selected_classifications, selected_fund_types, amc_filter, primary_type_filter, 
            period_options[selected_period], num_funds, display_type)

# Apply filters
def apply_filters(fund_profiles, available_amc, primary_type, 
                  selected_classifications, selected_fund_types, amc_filter, primary_type_filter):
    filtered_funds = fund_profiles

    if selected_classifications:
        filtered_funds = filtered_funds[filtered_funds['Classification Sector Scheme'].isin(selected_classifications)]

    if selected_fund_types:
        filtered_funds = filtered_funds[filtered_funds['Fund Type'].isin(selected_fund_types)]

    if amc_filter == "Only Tradable Companies":
        listed_amcs = available_amc['Fund Company'].dropna().unique()
        filtered_funds = filtered_funds[filtered_funds['Fund Company'].isin(listed_amcs)]

    if primary_type_filter == "Only Primary Types":
        primary_types = primary_type['SEC_CODE'].dropna().unique()
        filtered_funds = filtered_funds[filtered_funds['TH_CODE'].isin(primary_types)]

    return filtered_funds

# Calculate performance
def calculate_performance(filtered_nav, start_date, display_type, num_funds):
    if filtered_nav.empty:
        return pd.DataFrame(), []
    
    filtered_nav = filtered_nav.pivot(index='Date', columns='Fund Name', values='NAV')
    def cumulative_pct_change(column):
        # หา index แรกและสุดท้ายที่ไม่ใช่ NaN
        first_valid = column.first_valid_index()
        last_valid = column.last_valid_index()
        
        # Slice เฉพาะช่วงที่ไม่ใช่ NaN
        valid_data = column.loc[first_valid:last_valid]
        
        # คำนวณ pct change สะสม
        return valid_data.pct_change().cumsum() * 100

    cumulative_changes = filtered_nav.apply(cumulative_pct_change)
    last_cumulative_changes = cumulative_changes.apply(lambda col: col[col.last_valid_index()] if col.last_valid_index() is not None else None).sort_values(ascending=(display_type == "Bottom Performers"))
    selected_funds = last_cumulative_changes.index[:num_funds].tolist()
    melted_cumulative_changes = cumulative_changes.reset_index().melt(id_vars='Date', var_name='Fund Name', value_name='Pct Change')

    return melted_cumulative_changes[melted_cumulative_changes["Fund Name"].isin(selected_funds)], selected_funds

# Calculate statistics
def calculate_statistics(filtered_nav):
    filtered_nav = filtered_nav.pivot(index='Date', columns='Fund Name', values='Pct Change').reset_index()
    filtered_nav = filtered_nav.resample('W-FRI', on='Date').last().reset_index().melt(id_vars='Date', var_name='Fund Name', value_name='Pct Change')
    filtered_nav['Pct Change'] = filtered_nav['Pct Change'].diff()
    weekly_nav = filtered_nav
    pct_stats = weekly_nav.groupby('Fund Name')['Pct Change'].agg(['mean', 'std', 'min', 'max']).reset_index()
    sharpe_ratios = weekly_nav.groupby('Fund Name').apply(
        lambda x: (x['Pct Change'].mean() / x['Pct Change'].std()) if x['Pct Change'].std() != 0 else np.nan
    ).reset_index(name='Sharpe Ratio')

    return pd.merge(pct_stats, sharpe_ratios, on='Fund Name')

# Main app
fund_profiles, fund_nav, available_amc, primary_type = load_data()
fund_nav_long = prepare_nav_data(fund_nav)

(selected_classifications, selected_fund_types, amc_filter, primary_type_filter, 
 selected_period, num_funds, display_type) = create_sidebar(fund_profiles, available_amc, primary_type)

filtered_funds = apply_filters(fund_profiles, available_amc, primary_type, 
                               selected_classifications, selected_fund_types, amc_filter, primary_type_filter)

filtered_fund_names = filtered_funds['TH_CODE'].unique()
start_date = datetime.now() - selected_period
filtered_nav = fund_nav_long[(fund_nav_long['Fund Name'].isin(filtered_fund_names)) & (fund_nav_long['Date'] >= start_date)]
filtered_nav, selected_funds = calculate_performance(filtered_nav, start_date, display_type, num_funds)

#st.title("Fund Price Comparison")

if filtered_nav.empty:
    st.write("No data available for the selected filters.")
else:
    fig = px.line(
        filtered_nav, 
        x="Date", 
        y="Pct Change", 
        color="Fund Name",
        title="Fund Performance Comparison",
        labels={"Pct Change": "% Change from Start", "Date": "Date"}
    )
    
    fig.update_layout(
    width=1200,  # ความกว้างของกราฟ
    height=800,  # ความสูงของกราฟ
    title_font_size=32  # ขนาดฟอนต์ของชื่อกราฟ
    )
    st.plotly_chart(fig, use_container_width=True, width=1000, height=800)
    
    stats_summary = calculate_statistics(filtered_nav)
    stats_summary = stats_summary[stats_summary['Fund Name'].isin(selected_funds)].reset_index(drop=True)
    fund_profiles = fund_profiles.loc[:, ['Classification Sector Scheme', "Fund Type", "Fund Company", "Geographic Focus", "Total Net Assets", "Current Initial Charge", "Current Annual Charge"]]
    stats_summary.merge(fund_profiles, left_on='Fund Name', right_on='TH_CODE', how='left')

    st.header("Weekly Descriptive Statistics (%Pct_Chg) and Sharpe Ratio")
    st.dataframe(stats_summary, width=2000)
