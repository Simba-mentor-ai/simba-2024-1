import streamlit as st
import streamlit_authenticator as stauth
import yaml
import gettext
import random
import string
import options
from sidebar_loading import clearSidebar, loadSidebar
from yaml.loader import SafeLoader
import database_manager as dbm

_ = gettext.gettext

options.translate()

# hide_bar= """
#         <style>
#         [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
#             visibility:hidden;
#             width: 0px;
#         }
#         [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
#             visibility:hidden;
#         }
#         </style>
#     """

def getConfig():
    config = []

    with open('./auth_config/config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    return config

def saveConfig(config):
    with open('./auth_config/config.yaml', 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

def initAuth():
    st.session_state["auth_config"] = getConfig()
    
    st.session_state["authenticator"]  = stauth.Authenticate(
        st.session_state["auth_config"]['credentials'],
        st.session_state["auth_config"]['cookie']['name'],
        st.session_state["auth_config"]['cookie']['key'],
        st.session_state["auth_config"]['cookie']['expiry_days']
    )

def authenticate():

    clearSidebar()
    
    if "authenticator" not in st.session_state:
        initAuth()

    if "username" in st.session_state:
        st.session_state["oldUser"] = st.session_state["username"]

    if "auth_display" not in st.session_state :
        st.session_state["auth_display"] = "login"

    #Register new user
    if st.session_state["auth_display"] == "register" :

        if st.sidebar.button(_("Login"), use_container_width=True):
            st.session_state["auth_display"] = "login"
            st.rerun()

        email, username, name = st.session_state["authenticator"].register_user(preauthorization=False,
                                fields={ 'Form name': _('Register User'),
                                        'Username': _('Username'),
                                        'Email': _('Email'),
                                        'Password': _('Password'),
                                        'Repeat password': _('Repeat password'),
                                        'Register': _('Register') })
    
        if email:
            saveConfig(st.session_state["auth_config"])
            dbm.createUser(username,"student",name,email)
            st.session_state["auth_display"] = "login"
            st.rerun()

    #Forgot username
    elif st.session_state["auth_display"] == "fgusr" :
        username, email = st.session_state["authenticator"].forgot_username(fields = {'Form name': _('Forgot username'),
                                                                                                            'Email': _('Email'),
                                                                                                            'Submit': _('Submit')})

        if username:
            st.success('Username to be sent securely')
            # The developer should securely transfer the username to the user.
        elif username == False:
            st.error('Email not found')

    #Forgot password
    elif st.session_state["auth_display"] == "fgpwd" :
        username, email, new = st.session_state["authenticator"].forgot_password(fields = {'Form name': _('Forgot password'),
                                                                                                                                   'Username': _('Username'),
                                                                                                                                   'Submit': _('Submit')})
        if username:
            st.success('New password to be sent securely')
            # The developer should securely transfer the new password to the user.
        elif username == False:
            st.error('Username not found')


    #Login
    elif st.session_state["auth_display"] == "login" :



        emailr, username, name = st.session_state["authenticator"].login(
            fields = {
                'Form name':_('Login'), 
                'Username':_('Username'), 
                'Password':_('Password'), 
                'Login':_('Login')
                }
            )

        if st.session_state["authentication_status"] is None or st.session_state["authentication_status"] is False :

            # Display message
            if st.session_state["authentication_status"] is False:
                st.error(_('Username or password is incorrect'))
            elif st.session_state["authentication_status"] is None:
                st.warning(_('Please, login before using the application.'))

            #Buttons
            if st.sidebar.button(_("New user"), use_container_width=True):
                st.session_state["auth_display"] = "register"
                st.rerun()
            if st.sidebar.button(_("Forgot my password"), use_container_width=True):
                st.session_state["auth_display"] = "fgpwd"
                st.rerun()
            if st.sidebar.button(_("Forgot my username"), use_container_width=True):
                st.session_state["auth_display"] = "fgusr"
                st.rerun()

        # elif st.session_state["authentication_status"]:

        
def resetPwd():

    if "authenticator" not in st.session_state:
        initAuth()

    if st.session_state["authenticator"].reset_password(st.session_state["username"], fields = {'Form name': _('Reset password'),
                                                                                                'Current password': _('Current password'),
                                                                                                'New password': _('New password'),
                                                                                                'Repeat password': _('Repeat password'),
                                                                                                'Reset': _('Reset')}):
        saveConfig(st.session_state["auth_config"])
        st.success('Password modified successfully')

def updateUsr():

    if "authenticator" not in st.session_state:
        initAuth()

    if st.session_state["authenticator"].update_user_details(st.session_state["username"], fields = { 'Form name': _('Update user details'),
                                                                                                     'Field': _('Field'),
                                                                                                     'Name': _('Name'),
                                                                                                     'Email': _('Email'),
                                                                                                     'New value': _('New value'),
                                                                                                     'Update': _('Update') }):
        saveConfig(st.session_state["auth_config"])
        st.success('Entries updated successfully')

def initSession():
    if "session_initiated" not in st.session_state or not st.session_state["session_initiated"] or st.session_state["oldUser"] != st.session_state["username"]:
        st.session_state["UserRole"] = dbm.getRole(st.session_state["username"])
        loadSidebar()
        st.session_state["authenticator"].logout(location='sidebar')
        st.session_state["session_initiated"] = True

    else :
        st.session_state["authenticator"].logout(location='sidebar')