import streamlit as st
import edit_functions
import new_edit_template
import gettext
import options
import database_manager as dbm
from authentication import authenticate, initSession


_ = gettext.gettext

options.translate()

# My activities/
@st.experimental_dialog("Activity link")
def displayCode(code):
    # st.write("give this code to your students to give them access to the activity :")
    # st.markdown(code)
    st.write("give this url to your students to give them access to the activity  :")
    st.markdown(f"[share](/?code={code})")

if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    authenticate()

else:

    initSession()
    if (st.session_state["UserRole"]=="teacher" or st.session_state["UserRole"]=="admin"):

        if "assistants" not in st.session_state:
            st.session_state["assistants"] = edit_functions.getUserAssistants()


        if not "selectedID" in st.session_state:
            if len(list(st.session_state["assistants"].keys())) > 0 :
                st.session_state["selectedID"] = list(st.session_state["assistants"].keys())[0]
            else :
                st.session_state["selectedID"] = 0 

        st.write(_("# activities parameters"))

        col1, col2 = st.columns([0.2,0.8])

        with col1 :
            st.write(_("### activities"))

            asdict = st.session_state["assistants"]

            with st.container(border=True, height=500):

                if st.button(_("↺ refresh activities list")):
                    # st.session_state["assistants"] = edit_functions.getAssistants() 
                    st.session_state["assistants"] = edit_functions.getUserAssistants()
                    st.rerun()
                
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
            
            if st.button(_("delete selected activity"),type="primary", use_container_width=True):
                edit_functions.delAssistant(st.session_state["selectedID"])
                st.session_state["assistants"] = edit_functions.getUserAssistants()

            if st.button(_("get this activity's access link"), use_container_width=True):
                code = dbm.getActivityCode(st.session_state["selectedID"])
                displayCode(code)
                

        with col2 :
            st.write(_("### Selected activity"))

            if st.session_state["selectedID"] == 0:
                st.write(_("Please select an activity"))
            else :
                new_edit_template.loadTemplate(st.session_state["assistants"][st.session_state["selectedID"]])

    else :

        st.write("You were not supposed to access this page, please go back.")

