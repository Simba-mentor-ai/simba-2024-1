import streamlit as st
import edit_functions
import database_manager as dbm

if st.button("Cleanup files"):
    edit_functions.delfiles()

if st.button("Delete AIED users"):
    dbm.delAIEDUsers()

if st.button("Check AIED users"):
    dbm.checkAIEDUsers()

if st.button("Update activities"):
    dbm.updateActivities()