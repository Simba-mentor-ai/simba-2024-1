import streamlit as st
import streamlit_authenticator as stauth
from streamlit_config_helper import set_streamlit_page_config_once
from authentication import authenticate
import options
import gettext

_ = gettext.gettext

set_streamlit_page_config_once()

options.translate()

def selectLanguage() :
    selected = options.languages[0]
    if "SelectedLanguage" in st.session_state and st.session_state["SelectedLanguage"] :
        selected = st.session_state["SelectedLanguage"]
        if options.langCorrespondance[selected] != st.session_state["language"]:
            st.session_state["language"] = options.langCorrespondance[selected]
            st.rerun()
        
# if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:

authenticate()

# else :
if "authentication_status" in st.session_state and st.session_state["authentication_status"]:

    # #Language selection
    # lang,stuff = st.columns([0.15,0.85])
    # with lang:
    #     st.selectbox("Language", options=options.languages, index=options.langSymbols.index(st.session_state["language"]), on_change=selectLanguage(), key="SelectedLanguage", label_visibility="hidden")

    # Title of the webpage
    st.title(_("Welcome to SIMBA - your personal learning assistant"))

    # Using columns to place text and image side by side
    col1, col2 = st.columns(2)
    with col1:  # First column for the text
        st.markdown(_("""
        ## **SIMBA accompanies you in your learning**.

        SIMBA (Intelligent Mentoring, Wellbeing and Support System) has been designed to enhance your learning experience. 
                    
        Use SIMBA to review and reflect on questions related to course content, to organise yourself and create the best action plan to achieve the course objectives.
        """))
        

    with col2:  # Second column for the image
        st.image("SIMBA_img.jpeg", caption=_('SIMBA - Your Learning Partner'))

    st.markdown("---")

    # with st.sidebar :
        # if st.button("modify account")

    # Introduction and brief summary
    # st.markdown(_("""

    # ## **How to use SIMBA :**

    # """))
