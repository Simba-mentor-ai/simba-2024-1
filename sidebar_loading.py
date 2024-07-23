from st_pages import Page, show_pages, add_page_title, hide_pages
import streamlit as st
import options
import gettext

_ = gettext.gettext

options.translate()

def clearSidebar():
    # show_pages([Page("SIMBA.py", _("SIMBA main page"), "😸")])
    hide_pages([_("SIMBA main page"), _("New activity"), _("Edit activities"), _("My activities"), _("Manage my account")])

def loadSidebar():
    show_pages([
                Page("SIMBA.py", _("SIMBA main page"), "😸"),
                Page("sidebar/New_activity.py", _("New activity"), "➕"),
                Page("sidebar/Edit_activities.py", _("Edit activities"), "⚙️"),
                Page("sidebar/My_activities.py", _("My activities"), "📝"),
                Page("sidebar/Manage_account.py", _("Manage my account"), "👤"),
                # Page("sidebar/Admin.py", "Admin")
    ])
    if st.session_state["UserRole"]=="student":
        hide_pages([_("New activity"), _("Edit activities")])