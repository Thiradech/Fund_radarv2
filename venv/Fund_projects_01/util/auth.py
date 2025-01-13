from dotenv import load_dotenv
import streamlit as st
import os

# โหลด Environment Variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../Configuration/.env"))


# ฟังก์ชันตรวจสอบบทบาท
def authenticate_user(username, password):
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")
    return username == admin_username and password == admin_password

def get_user_role(username):
    admin_username = os.getenv("ADMIN_USERNAME")
    return "admin" if username == admin_username else "user"

def recheck_auth():
    if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
        st.error("Unauthorized access. Redirecting to Fundwiz...")
        st.query_params["page"] = "Fundwiz"
        st.stop()

    if st.session_state["role"] != "admin":
        st.error("Access denied. Redirecting to Fundwiz...")
        st.query_params["page"] = "Fundwiz"
        st.stop()
