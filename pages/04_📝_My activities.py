from streamlit_config_helper import set_streamlit_page_config_once

# set_streamlit_page_config_once()

from auth_helper import get_auth_status
import streamlit as st
import edit_functions
import chatpage_template


st.set_page_config(layout="wide")



if "Myactivities_initialized" not in st.session_state :
    st.session_state["Myactivities_initialized"] = False

if not st.session_state["Myactivities_initialized"]:
    st.session_state["activities"] = edit_functions.getAssistants()
    ids = st.session_state["activities"].keys()

    names = []
    for id in ids :
        names.append(st.session_state["activities"][id]["name"])

def selectActivity() :
    i = names.index(st.session_state["SelectedName"])
    st.session_state["selected activity"] = ids[i]
    st.rerun()

if "selected activity" not in st.session_state :
    st.session_state["selected activity"] = ""

st.write("# Activity")

st.selectbox("Select your activity", names, placeholder="select an activity...", on_change=selectActivity(), index="SelectedName")

activityContainer = st.container()
with activityContainer:
    if st.session_state["selected activity"]!="":
        if get_auth_status():
            assistant = st.session_state["activities"][st.session_state["selected activity"]]
            chatpage_template.load_template(
                activity_id=assistant["id"], 
                assistant_id=assistant["id"], 
                title=assistant["name"]
            )

st.session_state["Myactivities_initialized"] = True

    