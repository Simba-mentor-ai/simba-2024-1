from openai import OpenAI
import streamlit as st
from langchain_core.prompts import PromptTemplate
import edit_functions as ef
import re
import time
from datetime import datetime, date

attitudes = ["friendly","informal","formal"]
teachtypes = ["socratic","other"]
openai_client = OpenAI()




def loadTemplate(assistant):

    new = assistant == {}

    if "initialized" not in st.session_state :
        st.session_state["initialized"] = False

    if assistant!={} and not new :
        oldprompt = assistant["instructions"]
        vals = ef.extractVals(oldprompt)

    #Name
        name = st.text_input("Activity's new name", value = "" if new else assistant["name"], placeholder = "New name...")

    #Course
        course = st.text_input("Course's name", value = "" if new else vals["courseName"], placeholder = "New course name...")

    #Description
        desc = st.text_input("Modify the description or enter a new one", value = "" if new else assistant["description"], placeholder = "New description...")
    
    #Questions
    if not st.session_state["initialized"] :
        if new :
            st.session_state["nbQuestions"] = 1
            st.session_state["questions"] = [""]
        else :
            st.session_state["nbQuestions"] = vals["nbQuestions"]
            st.session_state["questions"] = vals["questions"]

    add,remove = st.columns([.5,1])
    with add:
        if st.button("➕ add a question") :
            st.session_state["nbQuestions"] = st.session_state["nbQuestions"]+1
    with remove:
        if st.button("➖ remove a question") :
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

    st.session_state["initialized"] = True

    cancel,submit = st.columns([.5,1])

    if not new :
        with cancel:
            if st.button("Cancel"):
                st.session_state["initialized"] = False
                st.rerun()
    with submit:
        if st.button("Submit"):
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
                openai_client.beta.assistants.create(name = name, description = desc, instructions = instructions)
                st.session_state["assistants"] = ef.getAssistants()
                st.session_state["initialized"] = False
                success("The new activity have been successfully created")

            else :
                openai_client.beta.assistants.update(assistant["id"], name = name, description = desc, instructions = instructions)
                st.session_state["assistants"] = ef.getAssistants()
                st.session_state["initialized"] = False
                success("The activity have been successfully updated")


@st.experimental_dialog("Success")
def success(line):
    st.write(line)
    st.button("ok", on_click=st.rerun())    