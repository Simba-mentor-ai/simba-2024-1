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

#TODO : delete the threads ?
def delActivitiy(id):

    activity = db.collection('activities').document(id)
    doc = activity.get()

    if doc.exists:
        dic = doc.to_dict()

        courseid = dic["course"]
        course = db.collection('courses').document(courseid)
        courseDoc = course.get()
        
        if courseDoc.exists :
            courseDic = courseDoc.to_dict()
            courseDic["activities"].remove(id)

        activity.delete()

def createUser(username, role):

    values = {"role" : role, "name" : "AIED test teacher", "courses" : []}            
    
    db.collection('users').document(username).create(values)

def deleteUser(username) :

    userdoc = db.collection('users').document(username).get()

    if userdoc.exists :
        userdic = userdoc.to_dict()
        role = userdic["role"]
        courses = userdic["courses"]

        for coursename in courses :

            coursedoc = db.collection('courses').document(coursename).get()

            if coursedoc.exists :
                coursedic = coursedoc.to_dict()

                if role == "teacher":
                    coursedic["teachers"].remove(username)

                elif role == "student":
                    coursedic["students"].remove(username)

                db.collection('courses').document(coursename).update(coursedic)
        
        userdoc = db.collection('users').document(username).delete()

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

    values = {"name" : activity.name, "course" : courseName}

    db.collection('activities').document(activity.id).create(values)

    course = db.collection('courses').document(courseName)
    courseDoc = course.get()

    if courseDoc.exists :
        courseDic = courseDoc.to_dict()

        courseDic["activities"].append(activity.id)

        course.update(courseDic)

def delAIEDUsers():

    coursedic = db.collection("courses").document("AIED").get().to_dict()
    teachers = coursedic["teachers"]

    print(teachers)

    for teacher in teachers :
        if teacher[0:4] == "AIED":
            print("deleting", teacher)
            deleteUser(teacher)