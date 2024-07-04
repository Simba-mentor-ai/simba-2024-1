import streamlit as st
import streamlit_authenticator as stauth
from streamlit_config_helper import set_streamlit_page_config_once
from auth_helper import get_auth_status
import options
import gettext
from sidebar_loading import loadSidebar

_ = gettext.gettext

set_streamlit_page_config_once()

if "language" not in st.session_state:
    st.session_state["language"] = "en"

elif st.session_state["language"] != "en" :
    localizator = gettext.translation('base', localedir='locales', languages=[st.session_state["language"]])
    localizator.install()
    _ = localizator.gettext 

def selectLanguage() :
    selected = options.languages[0]
    if "SelectedLanguage" in st.session_state and st.session_state["SelectedLanguage"] :
        selected = st.session_state["SelectedLanguage"]
        if options.langCorrespondance[selected] != st.session_state["language"]:
            st.session_state["language"] = options.langCorrespondance[selected]
            st.rerun()
        
    

if get_auth_status():

    st.session_state["UserType"]="teacher"

    loadSidebar()

    #Language selection
    lang,stuff = st.columns([0.15,0.85])
    with lang:
        st.selectbox("", options=options.languages, index=options.langSymbols.index(st.session_state["language"]), on_change=selectLanguage(), key="SelectedLanguage")

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

    # Introduction and brief summary
    st.markdown(_("""

    ## **How to use SIMBA :**

    """))
