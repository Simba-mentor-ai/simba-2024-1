import streamlit as st
import random
import string
import yaml
from yaml.loader import SafeLoader
from google.oauth2 import service_account
from google.cloud import firestore
from openai import OpenAI

openai_client = OpenAI()
GCP_PROJECT = st.secrets["GCP_PROJECT"]
creds = service_account.Credentials.from_service_account_info(st.secrets["FIRESTORE_CREDS"])
db = firestore.Client(credentials=creds, project=GCP_PROJECT)

# Activities
def delActivitiy(id):

    activity = db.collection('activities').document(id)
    doc = activity.get()

    if doc.exists:
        dic = doc.to_dict()
        codes = db.collection('utilities').document('activity_codes').get().to_dict()["codes"]
        code = dic["code"]

        usersids = dic["users"]

        for userId in usersids :

            user = db.collection('users').document(userId)
            userDoc = user.get()
        
            if userDoc.exists :
                userDic = userDoc.to_dict()
                userDic["activities"].remove(id)
                user.update(userDic)

        codes.pop(code, None)
        db.collection('utilities').document('activity_codes').update({"codes" : codes})
        activity.delete()

def createActivity(activity):

    codes = db.collection('utilities').document('activity_codes').get().to_dict()["codes"]
    code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
    while code in codes.keys():
        code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

    codes[code] = activity.id
    values = {"name" : activity.name, "users" : [st.session_state["username"]], "code" : code}

    db.collection('activities').document(activity.id).create(values)
    db.collection('utilities').document('activity_codes').update({"codes" : codes})
    addUserToActivity(activity.id,st.session_state["username"])

def getActivities(userName):

    user = db.collection('users').document(userName).get()
    activities = []

    if user.exists:
        activities = user.to_dict()["activities"]

    return activities

def getActivityCode(id):

    activity = db.collection('activities').document(id).get()

    if activity.exists :
        code = activity.to_dict()["code"]

    return code



# Users
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

def addUserFromCode(code,userName):

    codes = db.collection('utilities').document('activity_codes').get().to_dict()["codes"]
    activityName = codes[code]
    name = addUserToActivity(activityName, userName)
    return name

def addUserToActivity(activityName,userName):

    user = db.collection('users').document(userName)
    userDoc = user.get()
    activity = db.collection('activities').document(activityName)
    activityDoc = activity.get()

    if activityDoc.exists and userDoc.exists:

        activityDic = activityDoc.to_dict()
        userDic = userDoc.to_dict()

        if activityName not in userDic["activities"] :
            userDic["activities"].append(activityName)
            user.update(userDic)
        
        if userName not in activityDic["users"]:
            activityDic["users"].append(userName)
            activity.update(activityDic)
            
            return activityDic["name"]

def getRole(userName):

    role = "unknown"
    userDoc = db.collection('users').document(userName).get()
    if userDoc.exists :
        role = userDoc.get("role")
    
    return role


# Credentials
def getConfig():

    cred = db.collection("utilities").document("credentials").get().to_dict()

    config = cred["credentials"]

    return config

def saveConfig(config):
    cred = db.collection("utilities").document("credentials").get().to_dict()

    cred["credentials"] = config

    db.collection("utilities").document("credentials").update(cred)


# Admin special functions
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

    assistantsids = []

    for assistant in assistants :

        assistantsids.append(assistant.id)
        doc = db.collection('activities').document(assistant.id).get()

        if not doc.exists :

            values = values = {"name" : assistant.name, "users" : ["gabartas"]}

            db.collection('activities').document(assistant.id).create(values)

    db.collection('users').document('gabartas').update({"activities" : assistantsids})

def generateCodes():

    codes = db.collection('utilities').document('activity_codes').get().to_dict()["codes"]
    activities = db.collection('activities').get()

    for activity in activities :
        
        activitydic = activity.to_dict()

        code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
        while code in codes.keys():
            code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))
        
        activitydic["code"] = code
        codes[code] = activity.id

        db.collection('activities').document(activity.id).update(activitydic)

    db.collection('utilities').document('activity_codes').update({"codes" : codes})
