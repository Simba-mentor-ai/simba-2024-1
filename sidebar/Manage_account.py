import streamlit as st
import gettext
import options
import database_manager as dbm
from authentication import authenticate, updateUsr, resetPwd, initSession, initAuth

_ = gettext.gettext

if "authentication_status" not in st.session_state or not st.session_state["authentication_status"]:
    authenticate()

else:

    initSession()
    _ = options.translate(_)
    st.write("# Account settings page")

    if "authenticator" not in st.session_state:
        initAuth()

    try :
        if st.session_state["authenticator"].update_user_details(st.session_state["username"], fields = { 'Form name': _('Update user details'),
                                                                                                        'Field': _('Field'),
                                                                                                        'Name': _('Name'),
                                                                                                        'Email': _('Email'),
                                                                                                        'New value': _('New value'),
                                                                                                        'Update': _('Update') }):

            st.success('Informations modified successfully')
            dbm.saveConfig(st.session_state["auth_config"])  
            

    except Exception as e:
        st.error(e)

    try :
        if st.session_state["authenticator"].reset_password(st.session_state["username"], fields = {'Form name': _('Reset password'),
                                                                                                    'Current password': _('Current password'),
                                                                                                    'New password': _('New password'),
                                                                                                    'Repeat password': _('Repeat password'),
                                                                                                    'Reset': _('Reset')}):

            st.success('Password modified successfully')
            dbm.saveConfig(st.session_state["auth_config"])

    except Exception as e:
        st.error(e)