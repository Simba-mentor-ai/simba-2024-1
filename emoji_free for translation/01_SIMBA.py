import streamlit as st
import streamlit_authenticator as stauth
from streamlit_config_helper import set_streamlit_page_config_once
from auth_helper import get_auth_status
import gettext

_ = gettext.gettext

set_streamlit_page_config_once()

if get_auth_status():
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