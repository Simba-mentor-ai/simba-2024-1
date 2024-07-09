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

def getCourses(userName):

    user = db.collection('users').document(userName).get()
    courses = []

    if user.exists:
        courses = user.to_dict()["courses"]

    print(courses)
    return courses


def getActivities(courseName):

    course = db.collection('courses').document(courseName).get()
    activities = []

    if course.exists:
        activities = course.to_dict()["activities"]

    print(activities)
    return activities

def delAssistant(id):

    assistant = db.collection('activities').document(id)
    doc = assistant.get()

    if doc.exists:
        dic = doc.to_dict()

        courseid = dic["course"]
        course = db.collection('courses').document(courseid)
        courseDoc = course.get()
        
        if courseDoc.exists :
            courseDic = courseDoc.to_dict()
            courseDic["activities"].remove(id)

        assistant.delete()

def createUser(username, role):

    values = {"role" : role, "name" : "AIED test teacher", "courses" : []}            
    
    db.collection('users').document(username).create(values)

def addToCourse(userName,courseName):

    user = db.collection('users').document(userName)
    userDoc = user.get()
    course = db.collection('courses').document(courseName)
    courseDoc = course.get()

    if courseDoc.exists and userDoc.exists:
        role = userDoc.to_dict()["role"]
        courseDic = courseDoc.to_dict()
        userDic = userDoc.to_dict()
        if role == "teacher":
            courseDic["teachers"].append(userName)
        elif role == "student":
            courseDic["students"].append(userName)
        userDic["courses"].append(courseName)

        course.update(courseDic)
        user.update(userDic)

def addActivity(activity,courseName):

    # values = {"name" : activity.name, "threads" : {"active" : [], "inactive" : []}, "course" : courseName}

    # db.collection('activities').document(activity.id).create(values)

    course = db.collection('courses').document(courseName)
    courseDoc = course.get()

    if courseDoc.exists :
        courseDic = courseDoc.to_dict()

        courseDic["activities"].append(activity.id)

        course.update(courseDic)
