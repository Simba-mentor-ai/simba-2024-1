from openai import OpenAI
import streamlit as st
from langchain_core.prompts import PromptTemplate
import edit_functions as ef
import re
import time
from datetime import datetime, date

attitudes = ["friendly","informal","formal"]
teachtypes = ["socratic","other"]
accepted_extensions = [".c",".cs",".cpp",".doc",".docx",".html",".java",".json",".md",".pdf",".php",".pptx",".py",".rb",".tex",".txt",".css",".js",".sh",".ts"]
openai_client = OpenAI()




def loadTemplate(assistant):

    new = (assistant == {})

    if "initialized" not in st.session_state :
        st.session_state["initialized"] = False

    title = "Create a new activity"
    if not new :
        oldprompt = assistant["instructions"]
        vals = ef.extractVals(oldprompt)
        title = "Modify your activity"
        
    st.title(title)

    #Name
    name = st.text_input("Activity's new name", value = "" if new else assistant["name"], placeholder = "New name...")

    #Course
    course = st.text_input("Course's name", value = "" if new else vals["courseName"], placeholder = "New course name...")

    #Description
    desc = st.text_input("Modify the description or enter a new one", value = "" if new else assistant["description"], placeholder = "New description...")
    
    #Questions
    if not new and not st.session_state["initialized"] :
            st.session_state["nbQuestions"] = vals["nbQuestions"]
            st.session_state["questions"] = vals["questions"]
    else :
        if not st.session_state["initialized"] :
            st.session_state["nbQuestions"] = 1
            st.session_state["questions"] = [""]

    add,remove = st.columns([.3,1])
    with add:
        if st.button("➕ add a question") :
            st.session_state["nbQuestions"] = st.session_state["nbQuestions"]+1
    with remove:
        if st.button("➖ remove a question") and st.session_state["nbQuestions"]>1:
            st.session_state["nbQuestions"] = st.session_state["nbQuestions"]-1

    for i in range(1,st.session_state["nbQuestions"]+1):
        if i-1 < len(st.session_state["questions"]):
            st.session_state["questions"][i-1] = st.text_input(f"Question {i}", placeholder="enter the question statement", key=f"question{i}", value=st.session_state["questions"][i-1])
        else :
            st.session_state["questions"].append("")
            st.session_state["questions"][i-1] = st.text_input(f"Question {i}", placeholder="enter the question statement", key=f"question{i}")
    
    #prompt
    newprompt = PromptTemplate.from_template(ef.full_template)

    if new :
        advanced = st.expander("Advanced settings")
    else :
        advanced = st.container()
    
    with advanced:
        st.write("### Activity's assistant instructions :")

        #attitude
        adj1 = st.selectbox("What attitude should the assistant have toward the students ?", attitudes, index=0 if new else attitudes.index(vals["adj1"]))

        #teaching type
        teachtype = st.selectbox("What should be the assistant's approach to teaching ?", teachtypes, index=0 if new else teachtypes.index(vals["teaching_adj"]))

        #giving answers
        giveAnswers = st.checkbox("The assistant should give an answer to the activity questions if the student asks for it.", value=False if new else vals["answers"])

        #using emojis
        useEmojis = st.checkbox("The assistant should use emojis.", value=True if new else vals["emojis"])

        #mentioning documents
        mentiondocuments = st.checkbox("The assistant should encourage the student to rely on the provided documents for answering.", value=False if new else vals["documents"])
        if mentiondocuments:
            url = st.text_input("Is there an URL where to find those documents ?", value="" if new else vals["url"], placeholder="leave empty if you have no url")
        else :
            url = ""
        
        #word limit
        limit = st.number_input("include a word count limit for the assistant's answers ? (0 = no limit)", min_value=0, value=0 if new else vals["limits"])

    #Files
    if "files" not in st.session_state or not st.session_state["initialized"]:
        st.session_state["files"] = []

    file = st.file_uploader("Drop a file you want to add here", type=accepted_extensions)

    if st.button("Add file"):
        
        # Upload a file to OpenAI
        # LA piste !!! client.beta.assistants.files.list(assistant_id)
        if file :
            if new :
                st.session_state["files"].append(file)
                st.write("file added, to be uploaded upon activity creation.")
            else:
                status = st.status("Uploading file")
                # Add the uploaded file to the assistant
                # search if vector store exists :
                if "file_search" in dir(assistant["tool_resources"]) and len(assistant["tool_resources"].file_search.vector_store_ids)>0:
                        vid = assistant["tool_resources"].file_search.vector_store_ids[0]
                        openai_client.beta.vector_stores.files.upload(
                            vector_store_id=vid, file=file
                        )
                else :
                    vector_store = openai_client.beta.vector_stores.create(name=assistant["name"])
                    openai_client.beta.vector_stores.files.upload(
                        vector_store_id=vector_store.id, file=file
                    )   
                    status.update(label="Linking file to the activity")
                    openai_client.beta.assistants.update(assistant_id=assistant["id"],tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},)
                
                status.update(label="File added to the activity!",state="complete")
                st.session_state["assistants"] = ef.getAssistants()
                assistant = st.session_state["assistants"][st.session_state["selectedID"]]

            file = None

        else :
            error("please, add a file to be uploaded first.")

    st.session_state["initialized"] = True

    cancel,submit = st.columns([.5,1])

    if not new :
        with cancel:
            if st.button("Cancel"):
                st.session_state["initialized"] = False
                st.rerun()
    with submit:
        if st.button("Submit"):

            emptyquestion = False
            emptyI = 0
            for i in range(0,st.session_state["nbQuestions"]):
                if st.session_state["questions"][i] == "":
                    emptyquestion = True
                    emptyI = i
                    break

            if name == "":
                error("Please, give a name to your activity.")
            elif st.session_state["nbQuestions"] == 0 :
                error("The activity needs to have at least one question.")
            elif emptyquestion:
                error("The question " + str(emptyI+1) + " have no text.")

            else :
                instructions = newprompt.format(
                    courseName=course, 
                    teaching_adj=teachtype,
                    adj1 = adj1, 
                    emojis = ef.emojiGen(useEmojis),
                    questions = ef.questionsGen(),
                    answers = ef.answersGen(giveAnswers),
                    teaching_type = ef.teachTypeGen(teachtype),
                    documents = ef.docsGen(mentiondocuments, url),
                    limits= ef.limitsgen(limit)
                )
                if new :
                    status = st.status(label="Creating activity")
                    vector_store = None
                    if len(st.session_state["files"])>0 :
                        vector_store = openai_client.beta.vector_stores.create(name=name)
                        status.update(label = "uploading the files")
                    for f in st.session_state["files"] :
                        openai_client.beta.vector_stores.files.upload(
                            vector_store_id=vector_store.id, file=f
                        )
                    status.update(label="Creating activity")
                    if vector_store:
                        openai_client.beta.assistants.create(name = name, description = desc, instructions = instructions, tools=[{"type": "file_search"}], model="gpt-4-turbo",tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}})
                    else :
                        openai_client.beta.assistants.create(name = name, description = desc, instructions = instructions, tools=[{"type": "file_search"}], model="gpt-4-turbo")
                    success("The new activity have been successfully created")

                else :
                    openai_client.beta.assistants.update(assistant["id"], name = name, description = desc, instructions = instructions)
                    success("The activity have been successfully updated")
                
                


@st.experimental_dialog("Success")
def success(line):
    st.write(line)
    if st.button("ok"):
        st.session_state["assistants"] = ef.getAssistants()
        st.session_state["initialized"] = False   
        st.rerun() 

@st.experimental_dialog("Error")
def error(line):
    st.write(line)
    if st.button("ok"):
        st.rerun() 