import streamlit as st
import streamlit_authenticator as stauth
import yaml
import gettext
import random
import string
from yaml.loader import SafeLoader
import database_manager as dbm

_ = gettext.gettext



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
    config = getConfig()

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    return authenticator

def get_auth_status():

    
    config = getConfig()

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    
    # authenticator = initAuth

    if "displayRegister" not in st.session_state :
        st.session_state["displayRegister"] = False

    st.write(st.session_state["displayRegister"])

    if st.session_state["displayRegister"] :

        st.sidebar.button(_("Login"), on_click=displayRegister())

        authenticator.register_user(preauthorization=False,
                                fields={ 'Form name': _('Register User'),
                                        'Username': _('Username'),
                                        'Email': _('Email'),
                                        'Password': _('Password'),
                                        'Repeat password': _('Repeat password'),
                                        'Register': _('Register') })
    
        saveConfig(config)
        displayLogin()
        # st.rerun()

    else :
    
        st.sidebar.button(_("New user"), on_click=displayRegister())

        authenticator.login(
            fields = {
                'Form name':_('Login'), 
                'Username':_('University email'), 
                'Password':_('Password'), 
                'Login':_('Login')
                }
            )
        
        authentication_status = st.session_state['authentication_status']

        if authentication_status == False:
            st.error(_('Username or password is incorrect'))
            # st.markdown(hide_bar, unsafe_allow_html=True)

        elif authentication_status is None:
            st.warning(_('Please, login before using the application.'))
            # st.markdown(hide_bar, unsafe_allow_html=True)

        elif authentication_status == True:
            # # ---- SIDEBAR ----
            st.session_state["UserRole"] = dbm.getRole(st.session_state["username"])
            authenticator.logout(location='sidebar')

        return authentication_status


def displayRegister():
    st.session_state["displayRegister"] = not st.session_state["displayRegister"]

def displayLogin():
    st.session_state["displayRegister"] = False


def register(authenticator):

    config = getConfig()

    authenticator.register_user(preauthorization=False,
                                fields={ 'Form name': _('Register User'),
                                        'Username': _('Username'),
                                        'Email': _('Email'),
                                        'Password': _('Password'),
                                        'Repeat password': _('Repeat password'),
                                        'Register': _('Register') })
    
    saveConfig(config)

def AIED_authenticate():

    if 'authentication_status' not in st.session_state or st.session_state['authentication_status'] == False or "username" not in st.session_state :

        letters = string.ascii_letters

        userName = "AIED_"+"".join(random.choice(letters) for i in range(10))

        dbm.createUser(userName, "teacher")
        dbm.addToCourse(userName,"AIED")

        st.session_state['authentication_status'] = True
        st.session_state["UserRole"] = "teacher"
        st.session_state["username"] = userName

    return True