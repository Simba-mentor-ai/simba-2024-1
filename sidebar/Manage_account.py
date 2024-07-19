import streamlit as st
import gettext
import options
from authentication import authenticate, updateUsr, resetPwd, initSession

_ = gettext.gettext

options.translate()

if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    authenticate()

else:

    initSession()
    if (st.session_state["UserRole"]=="teacher" or st.session_state["UserRole"]=="admin"):
        st.write("# Account settings page")
        mainContainer = st.container()
        with st.sidebar :
            if st.button("Modify account details", use_container_width=True):
                with mainContainer :
                    updateUsr()
                    st.success('Entries updated successfully')
        with st.sidebar :
            if st.button("Modify password", use_container_width=True):
                with mainContainer :
                    resetPwd()
                    st.success('Password modified successfully')

    else :
        st.write("You were not supposed to access this page, please go back.")