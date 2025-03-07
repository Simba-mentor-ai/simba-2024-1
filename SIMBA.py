import streamlit as st
from streamlit_config_helper import set_streamlit_page_config_once
from authentication import authenticate, initSession
import options
import gettext
import database_manager as dbm

_ = gettext.gettext

set_streamlit_page_config_once()
        
if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    
    authenticate()

else:

    initSession()
    _ = options.translate(_)
    # #Language selection

    options.languageSelector()

    if "code" in st.query_params :
        name = dbm.addUserFromCode(st.query_params["code"],st.session_state["username"])
        st.success(_("The activity '{name}' have been added to your account.").format(name=name))

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
        st.image("SIMBA_img.jpeg", caption=_('SIMBA - Your Learning Partner'), width=300)

    st.markdown("---")


    # with st.sidebar :
    #     if st.button("Modify account details", use_container_width=True):
    #         updateUsr()
    #         st.success('Entries updated successfully')
    # with st.sidebar :
    #     if st.button("Modify password", use_container_width=True):
    #         resetPwd()
    #         st.success('Password modified successfully')

    # Introduction and brief summary
    # st.markdown(_("""

    # ## **How to use SIMBA :**

    # """))
