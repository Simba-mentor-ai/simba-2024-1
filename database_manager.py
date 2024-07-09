import streamlit as st
from google.oauth2 import service_account
from google.cloud import firestore

GCP_PROJECT = st.secrets["GCP_PROJECT"]
creds = service_account.Credentials.from_service_account_info(st.secrets["FIRESTORE_CREDS"])
db = firestore.Client(credentials=creds, project=GCP_PROJECT)

# Function to retrieve and compare the user password. return codes :
# 0 : valid check
# 1 : wrong password
# 2 : unknown user
# 3 : unknown error
# def checkPassword(usr,pwd):
#     userDoc = db.collection('courses').document(usr).get()
#     code = 3
#     if userDoc.exists :
#         if userDoc.
#     else :
#         code = 2
    
#     return code

def getRole(username):

    role = "unknown"
    userDoc = db.collection('users').document(username).get()
    if userDoc.exists :
        role = userDoc.get("role")
    
    return role