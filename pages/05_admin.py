import streamlit as st
import edit_functions

if st.button("Cleanup files"):
    edit_functions.delfiles()