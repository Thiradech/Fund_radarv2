import streamlit as st
from Fund_projects_01.util.auth import authenticate_user, get_user_role

# ระบบล็อกอินเฉพาะในหน้า Fundwiz
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["role"] = "guest"

if not st.session_state["authenticated"]:
    st.title("Fundwiz Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")
    for_Guest = st.button("For Guest") 

    if login_button:
        if authenticate_user(username, password):
            st.session_state["authenticated"] = True
            st.session_state["role"] = get_user_role(username)
            st.success("Login successful!")
            st.query_params["page"] = "Fundwiz"
        else:
            st.error("Invalid username or password.")
    if for_Guest:
        pass
else:
    st.title("Fundwiz Page")
    st.write("Welcome to the Fundwiz dashboard!")
    st.write(f"You are logged in as: {st.session_state['role']}")

    # แสดงลิงก์เฉพาะ Admin
    if st.session_state["role"] == "admin":
        st.markdown("### Admin Tools")
        st.markdown("- [Create Portfolio](?page=create_portfolios)")
        st.markdown("- [Trade Fund](?page=trade_fund)")
    else:
        st.info("You only have access to this page.")
    # ปุ่ม Logout
    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["role"] = "guest"
        st.query_params["page"] = "Fundwiz"
        
    
