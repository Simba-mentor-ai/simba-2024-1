import streamlit as st
import edit_functions
import new_edit_template
from authentication import authenticate

authenticate()

if "authentication_status" in st.session_state and st.session_state["authentication_status"]  and (st.session_state["UserRole"]=="teacher" or st.session_state["UserRole"]=="admin"):
    new_edit_template.loadTemplate({})

else :
    st.write("You were not supposed to access this page, please go back.")