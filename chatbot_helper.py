from google.oauth2 import service_account
from google.cloud import firestore
import openai
from openai import OpenAI
import streamlit as st
import logging
import time
import chatbot_eval as ce

openai.api_key = st.secrets["OPENAI_API_KEY"]
openai_client = OpenAI()

GCP_PROJECT = st.secrets["GCP_PROJECT"]
COURSE_ID = st.secrets["COURSE_ID"]

import json
creds = service_account.Credentials.from_service_account_info(st.secrets["FIRESTORE_CREDS"])
db = firestore.Client(credentials=creds, project=GCP_PROJECT)

def disable_activity_threads(activity_id):
    users_db = db.collection('courses').document(str(COURSE_ID)).collection('users')
    users = users_db.get()
    for user in users :
        threads = user.collection('activity_threads').document(activity_id).get()
        if threads.exists:
            dic = threads.to_dict()
            for i in range(len(dic["threads"])):
                if dic["threads"][i]["active"] :
                    dic["threads"][i]["active"] = False

            user.collection('activity_threads').document(activity_id).set(dic)



def get_activity_thread(activity_id):
    user_id = st.session_state['username']
    course_db = db.collection('courses').document(str(COURSE_ID))
    users_db = course_db.collection('users')
    user_db = users_db.document(str(user_id))

    # Get thread_id from Firebase
    ua_threads = user_db.collection('activity_threads').document(activity_id).get()

    tid = 0
    # If the document does not exists, create it with a new thread
    if not ua_threads.exists:
        thread = openai_client.beta.threads.create()
        ua_threads.set({'threads': [{'id':thread.id, 'active' : True}]})
        create_message("Hola!", thread.id, activity_id)
        tid = thread.id

    else :
        dic = ua_threads.to_dict()
        # If old version, create new thread and update
        if 'threads' not in dic.keys():
            old_id = dic['thread_id']
            thread = openai_client.beta.threads.create()
            ua_threads.set({'threads': [{'id':old_id, 'active' : False},{'id':thread.id, 'active' : True}]})
            tid = thread.id

        # If current, just retrieve the active thread id
        else :
            for t in dic['threads']:
                if t["active"]:
                    tid = t["id"]
                    break

            # If no active thread found, create a new one :
            if tid == 0:
                threads = dic['threads']
                thread = openai_client.beta.threads.create()
                threads.append({'id' : thread.id, 'active' : True})
                ua_threads.set({'threads' : threads})
                tid = thread.id

    return tid

    # OLD VERSION :
    # activity_thread = user_db.collection('activity_threads').document(activity_id)

    # # If thread_id is None, create a new thread
    # activity_thread_exists = activity_thread.get().exists
    # if not activity_thread_exists:
    #     thread = openai_client.beta.threads.create()
    #     activity_thread.set({'thread_id': thread.id})
    #     create_message("Hola!", thread.id, activity_id)

    # return activity_thread.get().get('thread_id')


def get_messages(thread_id):
    # Get messages from thread

    messages = openai_client.beta.threads.messages.list(
         thread_id=thread_id,
         order="asc",
         limit=100
    )
    
    clean_messages = []
    for message in messages.data[1:]:
        # print(message)
        # print(message.content[0].text.annotations)
        new_message = {
            "role": message.role if message.role == "user" else "model",
            "content": message.content[0].text.value
        }
        clean_messages.append(new_message)


    # Reassign roles to messages
    return clean_messages


def create_message(input_message, thread_id, assistant_id):
    message = openai_client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=input_message,
    )

    logging.info('Starting run...')
    # The assistant's id belongs to the run, not the thread
    run = openai_client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    logging.info('Checking run status...')
    run = openai_client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run.id
    )
    
    while run.status not in ["completed", "failed", "cancelled", "expired"]:
        run = openai_client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        time.sleep(.1)

    logging.info('Run completed.')

    messages = openai_client.beta.threads.messages.list(
            thread_id=thread_id,
    )
    response_message = messages.data[0].content[0].text.value
    # print("New message :")
    # print(messages.data[0].content[0].text.annotations)
    logging.info(f'Response message: {response_message}')
    return response_message