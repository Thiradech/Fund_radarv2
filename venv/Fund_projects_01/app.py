import streamlit as st
import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

st.title("Welcome to Fund Radar")
st.write("เลือกหน้าใน sidebar เพื่อดูเนื้อหา!")
