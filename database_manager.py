import streamlit as st
from google.oauth2 import service_account
from google.cloud import firestore
from openai import OpenAI

openai_client = OpenAI()
GCP_PROJECT = st.secrets["GCP_PROJECT"]
creds = service_account.Credentials.from_service_account_info(st.secrets["FIRESTORE_CREDS"])
db = firestore.Client(credentials=creds, project=GCP_PROJECT)

def getRole(userName):

    role = "unknown"
    userDoc = db.collection('users').document(userName).get()
    if userDoc.exists :
        role = userDoc.get("role")
    
    return role

def getActivities(userName):

    user = db.collection('users').document(userName).get()
    activities = []

    if user.exists:
        activities = user.to_dict()["activities"]

    return activities


def delActivitiy(id):

    activity = db.collection('activities').document(id)
    doc = activity.get()

    if doc.exists:
        dic = doc.to_dict()

        usersids = dic["users"]

        for userId in usersids :

            user = db.collection('users').document(userId)
            userDoc = user.get()
        
            if userDoc.exists :
                userDic = userDoc.to_dict()
                userDic["activities"].remove(id)
                user.update(userDic)

        activity.delete()

def createUser(username, role, name, email):

    values = {"role" : role, "name" : name, "email" : email, "activities" : []}
    db.collection('users').document(username).create(values)

def modifyUser(username, role, name, email):
    
    values = {"role" : role, "name" : name, "email" : email}
    db.collection('users').document(username).update(values)

def deleteUser(username) :

    userdoc = db.collection('users').document(username).get()

    if userdoc.exists :
        userdic = userdoc.to_dict()
        role = userdic["role"]
        activities = userdic["activities"]

        for activityName in activities :

            activityDoc = db.collection('activities').document(activityName).get()

            if activityDoc.exists :
                activityDic = activityDoc.to_dict()

                activityDic["users"].remove(username)

                db.collection('activities').document(activityName).update(activityDic)
        
        userdoc = db.collection('users').document(username).delete()

def createActivity(activity):

    values = {"name" : activity.name, "users" : [st.session_state["username"]]}
    db.collection('activities').document(activity.id).create(values)

def addUserToActivity(activityName,userName):

    user = db.collection('users').document(userName)
    userDoc = user.get()
    activity = db.collection('activities').document(activityName)
    activityDoc = activity.get()

    if activityDoc.exists and userDoc.exists:

        activityDic = activityDoc.to_dict()
        userDic = userDoc.to_dict()
        role = userDic["role"]

        activityDic["users"].append(userName)
        userDic["activities"].append(activityName)

        activity.update(activityDic)
        user.update(userDic)

def updateActivities():
    
    activities = db.collection('activities').get()

    for activity in activities :
        
        dic = activity.to_dict()

        if "users" not in dic.keys() :

            if "name" in dic.keys():
                values = {"name" : dic["name"], "users" : [st.session_state["username"]]}
            else :
                values = {"name" : "defaultName", "users" : [st.session_state["username"]]}

            db.collection('activities').document(activity.id).set(values)
        
    assistants = openai_client.beta.assistants.list()

    for assistant in assistants :

        doc = db.collection('activities').document(assistant.id).get()

        if not doc.exists :

            values = values = {"name" : assistant.name, "users" : ["gabartas"]}

            db.collection('activities').document(assistant.id).create(values)
