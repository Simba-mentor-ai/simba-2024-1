import streamlit as st
import streamlit_authenticator as stauth
import gettext
import options
import emails
from sidebar_loading import clearSidebar, loadSidebar
import database_manager as dbm

_ = gettext.gettext

_ = options.translate(_)

def initAuth():
    st.session_state["auth_config"] = dbm.getConfig()
    
    st.session_state["authenticator"]  = stauth.Authenticate(
        st.session_state["auth_config"]['credentials'],
        st.session_state["auth_config"]['cookie']['name'],
        st.session_state["auth_config"]['cookie']['key'],
        st.session_state["auth_config"]['cookie']['expiry_days']
    )

#Function to be used on every page
def authenticate():
    _ = gettext.gettext
    _ = options.translate(_)
    clearSidebar()
    
    if "authenticator" not in st.session_state:
        initAuth()

    if "username" in st.session_state:
        st.session_state["oldUser"] = st.session_state["username"]

    #State indicating the page to display
    if "auth_display" not in st.session_state :
        st.session_state["auth_display"] = "login"

    #Register new user
    if st.session_state["auth_display"] == "register" :
        if st.sidebar.button(_("Login"), use_container_width=True):
            st.session_state["auth_display"] = "login"
            st.rerun()

        try:
            email, username, name = st.session_state["authenticator"].register_user(
                                    fields={ 'Form name': _('Register User'),
                                            'Username': _('Username'),
                                            'Email': _('Email'),
                                            'Password': _('Password'),
                                            'Repeat password': _('Repeat password'),
                                            'Register': _('Register') })
        
            if email:
                dbm.saveConfig(st.session_state["auth_config"])
                dbm.createUser(username,"student",name,email)
                st.session_state["auth_display"] = "login"
                st.rerun()
        except Exception as e:
            st.error(e)

    #Forgot username
    elif st.session_state["auth_display"] == "fgusr" :
        if st.sidebar.button(_("Login"), use_container_width=True):
            st.session_state["auth_display"] = "login"
            st.rerun()

        username, email = st.session_state["authenticator"].forgot_username(fields = {'Form name': _('Forgot username'),
                                                                                                            'Email': _('Email'),
                                                                                                            'Submit': _('Submit')})

        if username:
            message = _("""Hello, this is SIMBA recovery \n
Your username is {name}. \n
Please, delete this message after receiving it to ensure it is not stolen.""").format(name=username)
            emails.send_email_gmail(_("username recovery"),message,email)
            st.success(_('An email with your username have been sent to you, remember to check your spam folder if you cannot find it'))

        elif username == False:
            st.error(_('Email not found'))

    #Forgot password
    elif st.session_state["auth_display"] == "fgpwd" :
        if st.sidebar.button(_("Login"), use_container_width=True):
            st.session_state["auth_display"] = "login"
            st.rerun()

        username, email, newPwd = st.session_state["authenticator"].forgot_password(fields = {'Form name': _('Forgot password'),
                                                                                                                                   'Username': _('Username'),
                                                                                                                                   'Submit': _('Submit')})
        if username:
            message = _("""Hello, this is SIMBA recovery \n
Your randomly generated password is {password}. \n
Please, modify it as soon as possible from the main page to ensure it is not stolen.""").format(password=newPwd)
            emails.send_email_gmail(_("new password"),message,email)
            dbm.saveConfig(st.session_state["auth_config"])
            st.success(_('An email with a new password have been sent to you, remember to check your spam folder if you cannot find it'))
        elif username == False:
            st.error(_('Username not found'))


    #Login
    elif st.session_state["auth_display"] == "login" :


        st.session_state["authenticator"].login(
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
        st.success('Password modified successfully')
        dbm.saveConfig(st.session_state["auth_config"])

def updateUsr():

    if "authenticator" not in st.session_state:
        initAuth()

    if st.session_state["authenticator"].update_user_details(st.session_state["username"], fields = { 'Form name': _('Update user details'),
                                                                                                     'Field': _('Field'),
                                                                                                     'Name': _('Name'),
                                                                                                     'Email': _('Email'),
                                                                                                     'New value': _('New value'),
                                                                                                     'Update': _('Update') }):
        st.success('Entries updated successfully')
        dbm.saveConfig(st.session_state["auth_config"])

def initSession():
    if "session_initiated" not in st.session_state or not st.session_state["session_initiated"] or st.session_state["oldUser"] != st.session_state["username"]:
        st.session_state["UserRole"] = dbm.getRole(st.session_state["username"])
        loadSidebar()
        st.session_state["authenticator"].logout(location='sidebar')
        st.session_state["session_initiated"] = True

    else :
        st.session_state["authenticator"].logout(location='sidebar')