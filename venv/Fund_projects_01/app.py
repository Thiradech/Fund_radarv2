import streamlit as st
import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

st.set_page_config(page_title="Fund Radar", page_icon=":chart_with_upwards_trend:", layout="wide")
st.title("Welcome to Fund Radar")
st.write("เลือกหน้าใน sidebar เพื่อดูเนื้อหา!")
