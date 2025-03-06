import streamlit as st
import edit_functions
import emails
import database_manager as dbm

if st.button("Cleanup files"):
    edit_functions.delfiles()

if st.button("Update activities"):
    dbm.updateActivities()

if st.button("generate activity codes"):
    dbm.generateCodes()

if st.button("test email"):
    emails.send_email_gmail("SIMBA test", "If you can read this, it worked", "gabriel.ferrettini@gmail.com")

if st.button("cleanupAIED"):
    dbm.delAIEDUsers()

st.text_input("enter ID",key="idToDelete")
if st.button("delete user"):
    dbm.delUser(st.session_state["idToDelete"])