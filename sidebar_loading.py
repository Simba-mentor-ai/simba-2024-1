from st_pages import Page, show_pages, add_page_title, hide_pages
import streamlit as st
import options
import gettext

_ = gettext.gettext

options.translate()

def clearSidebar():
    show_pages([Page("SIMBA.py", _("SIMBA main page"), "😸")])

def loadSidebar():
    if st.session_state["UserRole"]=="teacher":
        show_pages([
                Page("SIMBA.py", _("SIMBA main page"), "😸"),
                Page("sidebar/New_activity.py", _("New activity"), "➕"),
                Page("sidebar/Edit_activities.py", _("Edit activities"), "⚙️"),
                Page("sidebar/My_activities.py", _("My activities"), "📝"),
                Page("sidebar/Admin.py", "Admin")
        ])
    else :
        show_pages([
                Page("SIMBA.py", _("SIMBA main page"), "😸"),
                Page("sidebar/My_activities.py", _("My activities"), "📝"),
        ])
        # hide_pages([_("New activity"),_("Edit activities")])