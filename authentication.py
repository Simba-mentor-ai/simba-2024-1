import streamlit as st
import gettext
import options
from sidebar_loading import clearSidebar, loadSidebar
import database_manager as dbm

_ = gettext.gettext

_ = options.translate(_)

#Function to be used on every page
def authenticate():
    _ = gettext.gettext
    _ = options.translate(_)
    clearSidebar()
    
    st.info(_("Please, enter a username for this session"))
    name = st.text_input(_("Name"))
    if st.button(_("Submit")):
        workshop_authenticate(name)

def initSession():
    if "session_initiated" not in st.session_state or not st.session_state["session_initiated"] or st.session_state["oldUser"] != st.session_state["username"]:
        st.session_state["UserRole"] = dbm.getRole(st.session_state["username"])
        loadSidebar()
        st.session_state["session_initiated"] = True

def workshop_authenticate(name):

    if 'authentication_status' not in st.session_state or st.session_state['authentication_status'] == False or "username" not in st.session_state :

        userName = "AIED_"+name


        dbm.createUser(userName, "teacher")

        st.session_state['authentication_status'] = True
        st.session_state["UserRole"] = "teacher"
        st.session_state["username"] = userName

    return True