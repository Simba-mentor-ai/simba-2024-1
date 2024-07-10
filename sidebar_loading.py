from st_pages import Page, show_pages, add_page_title, hide_pages
import streamlit as st

def loadSidebar():
    show_pages([
            Page("SIMBA.py", "SIMBA main page", "😸"),
            Page("sidebar/New_activity.py", "New activity", "➕"),
            Page("sidebar/Edit_activities.py", "Edit activities", "⚙️"),
            Page("sidebar/My_activities.py", "My activities", "📝"),
            # Page("sidebar/Admin.py", "Admin")
    ])
    if st.session_state["UserRole"]=="student":
        hide_pages(["New activity","Edit activities"])