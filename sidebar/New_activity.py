import streamlit as st
import edit_functions
import new_edit_template
from authentication import authenticate, initSession

if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    authenticate()

else:

    initSession()
    if (st.session_state["UserRole"]=="teacher" or st.session_state["UserRole"]=="admin"):
        new_edit_template.loadTemplate({})

    else :
        st.write("You were not supposed to access this page, please go back.")