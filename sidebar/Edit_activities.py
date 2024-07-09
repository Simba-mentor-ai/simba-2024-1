import streamlit as st
import edit_functions
import new_edit_template
import gettext

_ = gettext.gettext

st.set_page_config(layout="wide")

if "assistants" not in st.session_state:
        # st.session_state["assistants"] = edit_functions.getAssistants()
        st.session_state["assistants"] = edit_functions.getUserAssistants(st.session_state["username"])

if not "selectedID" in st.session_state:
        st.session_state["selectedID"] = list(st.session_state["assistants"].keys())[0]

st.write(_("# activities parameters"))

col1, col2 = st.columns([0.2,0.8])

with col1 :
    st.write(_("### activities"))

    asdict = st.session_state["assistants"]

    with st.container(border=True, height=500):

        if st.button(_("↺ refresh activities list")):
            # st.session_state["assistants"] = edit_functions.getAssistants() 
            st.session_state["assistants"] = edit_functions.getUserAssistants(st.session_state["username"])
        
        if asdict == {}:
             st.write("No activities created yet!")
        else : 
            for id in asdict :
                if st.session_state["selectedID"] == id :
                    t = "primary"
                else :
                    t = "secondary"
                
                if st.button(label = asdict[id]["name"], type=t, use_container_width=True, key=id):
                    st.session_state["selectedID"] = id
                    st.session_state["initialized"] = False
                    st.rerun()
    
    if st.button(_("delete selected activity"),type="primary"):
        edit_functions.delAssistant(st.session_state["assistants"][st.session_state["selectedID"]])

with col2 :
    st.write(_("### Selected activity"))

    if st.session_state["selectedID"] == 0:
        st.write(_("Please select an activity"))
    else :
        new_edit_template.loadTemplate(st.session_state["assistants"][st.session_state["selectedID"]])

