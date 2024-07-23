from st_pages import Page, show_pages, hide_pages
import streamlit as st
import options
import gettext

_ = gettext.gettext

_ = options.translate(_)

def clearSidebar():
    # show_pages([Page("SIMBA.py", _("SIMBA main page"), "😸")])
    hide_pages(["SIMBA main page", "New activity", "Edit activities", "My activities", "Manage my account"])

def loadSidebar():
    show_pages([
                Page("SIMBA.py", "SIMBA main page", "😸"),
                Page("sidebar/New_activity.py", "New activity", "➕"),
                Page("sidebar/Edit_activities.py", "Edit activities", "⚙️"),
                Page("sidebar/My_activities.py", "My activities", "📝"),
                Page("sidebar/Manage_account.py", "Manage my account", "👤"),
                # Page("sidebar/Admin.py", "Admin")
    ])
    if st.session_state["UserRole"]=="student":
        hide_pages(["New activity", "Edit activities"])