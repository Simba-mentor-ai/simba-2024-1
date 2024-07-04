from st_pages import Page, show_pages, add_page_title
import streamlit as st

def loadSidebar():
    
    if st.session_state["UserType"]=="student":
        show_pages([
            Page("SIMBA.py", "SIMBA main page", "😸"),
            Page("sidebar/My_activities.py", "My activities", "📝")
            ])
    elif st.session_state["UserType"]=="teacher":
        show_pages([
            Page("SIMBA.py", "SIMBA main page", "😸"),
            Page("sidebar/New_activity.py", "New activity", "➕"),
            Page("sidebar/Edit_activities.py", "Edit activities", "⚙️"),
            Page("sidebar/My_activities.py", "My activities", "📝")
        ])