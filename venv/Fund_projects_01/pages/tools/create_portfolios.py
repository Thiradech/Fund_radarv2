import streamlit as st
import csv
from Fund_projects_01.util.auth import recheck_auth
import os
st.write("hello")
st.write(st.session_state["authenticated"])
recheck_auth()

def join_path(relative_path):
    base_dir = os.path.dirname(__file__)
    return os.path.join(base_dir+"/..", relative_path)

def save_portfolio(portfolio_name, initial_balance):
    with open(f"{join_path('data/portfolios.csv')}", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([portfolio_name, initial_balance])

st.set_page_config(page_title="Create Portfolio Tool", layout="wide")
st.title("Create Portfolio")

# เนื้อหาของหน้า
st.title("Create Portfolio")
st.write("This page is restricted to admins.")

portfolio_name = st.text_input("Portfolio Name:")
initial_balance = st.number_input("Initial Balance:", min_value=0.0, step=0.01)

if st.button("Create Portfolio"):
    if portfolio_name:
        st.success(f"Portfolio '{portfolio_name}' created successfully!")
    else:
        st.error("Portfolio name cannot be empty.")
