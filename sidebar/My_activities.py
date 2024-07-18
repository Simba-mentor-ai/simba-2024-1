from streamlit_config_helper import set_streamlit_page_config_once

# set_streamlit_page_config_once()

from auth_helper import get_auth_status
import streamlit as st
import edit_functions
import chatpage_template
import gettext
import datetime
import options
from authentication import authenticate

_ = gettext.gettext

options.translate()

authenticate()

if "authentication_status" in st.session_state and st.session_state["authentication_status"]:
    today = datetime.date.today()

    # st.session_state["assistants"] = edit_functions.getAssistants()
    if "assistants" not in st.session_state :
        st.session_state["assistants"] = edit_functions.getUserAssistants()

    ids = st.session_state["assistants"].keys()
    names = []
    for id in ids :
        activity = st.session_state["assistants"][id]
        if st.session_state["UserRole"] == "teacher":
            names.append(activity["name"])
        
        elif st.session_state["UserRole"] == "student":
            startCheck = True
            endCheck = True

            if "startDate" in activity["metadata"] and today< datetime.datetime.strptime(activity["metadata"]["startDate"],"%Y/%m/%d").date():
                startCheck = False
            if "endDate" in activity["metadata"] and today> datetime.datetime.strptime(activity["metadata"]["endDate"],"%Y/%m/%d").date():
                endCheck = False

            if startCheck and endCheck:
                names.append(activity["name"])

    def selectActivity() :
        if "SelectedName" in st.session_state and st.session_state["SelectedName"] != None:
            i = names.index(st.session_state["SelectedName"])
            st.session_state["selected activity"] = list(ids)[i]

    if "selected activity" not in st.session_state :
        st.session_state["selected activity"] = ""

    st.write(_("# Activity"))

    st.selectbox(_("Select the activity you want to work on"), options=names, index=None, placeholder=_("select an activity..."), on_change=selectActivity(), key="SelectedName")

    activityContainer = st.container()
    with activityContainer:
        if st.session_state["selected activity"]!="" and st.session_state["SelectedName"] != None:
            # if get_auth_status():
                assistant = st.session_state["assistants"][st.session_state["selected activity"]]
                chatpage_template.load_template(
                    activity_id=assistant["id"],
                    assistant_id=assistant["id"],
                    title=assistant["name"]
                )

    