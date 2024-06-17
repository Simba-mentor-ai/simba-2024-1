import streamlit as st
import edit_functions
import new_edit_template

st.set_page_config(layout="wide")

if "assistants" not in st.session_state:
        st.session_state["assistants"] = edit_functions.getAssistants()

if not "selectedID" in st.session_state:
        st.session_state["selectedID"] = list(st.session_state["assistants"].keys())[0]

st.write("# activities parameters")

col1, col2 = st.columns([0.2,0.8])

with col1 :
    st.write("### activities")

    asdict = st.session_state["assistants"]

    with st.container(border=True, height=500):

        if st.button("↺ refresh activities list"):
            st.session_state["assistants"] = edit_functions.getAssistants() 
        
        for id in asdict :
            if st.session_state["selectedID"] == id :
                t = "primary"
            else :
                t = "secondary"
            
            if st.button(label = asdict[id]["name"], type=t, use_container_width=True, key=id):
                st.session_state["selectedID"] = id
                st.session_state["initialized"] = False
                st.rerun()
    
    if st.button("delete selected activity",type="primary"):
        edit_functions.delAssistant(st.session_state["assistants"][st.session_state["selectedID"]])

with col2 :
    st.write("### Selected activity")

    if st.session_state["selectedID"] == 0:
        st.write("Please select an activity")
    else :
        new_edit_template.loadTemplate(st.session_state["assistants"][st.session_state["selectedID"]])