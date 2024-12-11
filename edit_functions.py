from openai import OpenAI
import streamlit as st
import re
import gettext
import options
import database_manager as dbm
from traces_helper import save_navigation

_ = gettext.gettext
openai_client = OpenAI()

_ = options.translate(_)

attitudes = [_("friendly"),_("informal"),_("formal")]
teachtypes = [_("socratic"),_("other")]

def getAssistants():
    
    assistantslist = openai_client.beta.assistants.list()
    assistants = {}

    for a in assistantslist :
        newassistant = {}
        # print(dir(a))
        newassistant["id"] = a.id
        newassistant["name"] = a.name
        newassistant["model"] = a.model
        newassistant["description"] = a.description
        newassistant["instructions"] = a.instructions
        newassistant["metadata"] = a.metadata
        if("tool_resources" in dir(a)):
            newassistant["tool_resources"] = a.tool_resources
        else :
            newassistant["tool_resources"] = {}

        assistants[a.id] = newassistant

    return assistants

def getUserAssistants():

    activities = dbm.getActivities(st.session_state["username"])
    
    assistants = {}
    for activity in activities:
        newassistant = {}
        a = openai_client.beta.assistants.retrieve(activity)

        newassistant["id"] = a.id
        newassistant["name"] = a.name
        newassistant["model"] = a.model
        newassistant["description"] = a.description
        newassistant["instructions"] = a.instructions
        newassistant["metadata"] = a.metadata
        if("tool_resources" in dir(a)):
            newassistant["tool_resources"] = a.tool_resources
        else :
            newassistant["tool_resources"] = {}
        
        assistants[a.id] = newassistant

    return assistants

#Delete activity
@st.experimental_dialog("Are you sure ?")
def delAssistant(id):
    st.write("If you click 'ok', this assistant will be deleted permanently, no recovery will be possible")

    cancel,ok = st.columns([1,0.5])

    with cancel :
        if st.button("cancel"):
            st.rerun()

    with ok :
        if st.button("ok") :
            dbm.delActivitiy(id)
            openai_client.beta.assistants.delete(id) 
            save_navigation(id, "deleted")
            st.session_state["assistants"] = getUserAssistants()
            st.session_state["selectedID"] = 0 
            st.session_state["nbQuestions"] = 1
            st.session_state["questions"] = [""]
            st.session_state["initialized"] = False 
            st.rerun()  

def setSelectedid(i):
    st.session_state["selectedID"] = i  

#Modifying the main prompt :

full_template =_("""You are a {adj1} {teaching_adj} tutor for the course '{courseName}'.

Your name is SIMBA 😸 (Sistema Inteligente de Medición, Bienestar y Apoyo) and you were created by the Núcleo Milenio de Educación Superior and IRIT Talent team.
Respond in a {adj1}, concise and proactive way{emojis}.

Help the student answer the following questions:

{questions}

{subjects}

{answers} {teaching_type}

{documents}

Your first message should begin with ‘Hello! 😸 I am SIMBA, and I will help you reflect on the following questions: ’ Followed by the questions to answer.

{limits}""")

def limitsgen(limit):
    nstr = ""
    if limit != 0:
        nstr = _("Your answers should be {limit} words maximum.").format(limit=limit)
    return nstr
    
def docsGen(mentiondocuments, url):
    nstr = ""
    if mentiondocuments :
        nstr = _("Encourage them to go and read a section of the provided documents to answer.")
        if url != "":
            nstr += _(" If they do not have access to the text, they can find it at '{url}'.").format(url=url)
    return nstr

def teachTypeGen(type):
    nstr = ""

    if type == _("socratic"):
        nstr = _("Act as a Socratic tutor, taking the initiative in getting the students to answer the questions.")
    else :
        nstr = _("Act as a standard teacher.")
    return nstr

def answersGen(give):
    nstr = ""
    if give :
        nstr = _("You should not give the answer, but guide the student to answer.")
    else:
        nstr = _("You can provide an answer to the provided questions if the student asks for it.")
    return nstr

def questionsGen():
    nstr = ""

    for i in range(1,st.session_state["nbQuestions"]+1):
        nstr = nstr + _("Question {i} : {question} \n").format(i=i, question = st.session_state[f'question{i}'])

    return nstr

def subjectsGen(subjects, restricted):
    nstr = ""

    if subjects!="":
        nstr += _("You should help the student to reflect in depth on the following course subjects :\n <Beginning of the course subjects>\n")
        nstr += subjects
        nstr += _("\n<end of the course subjects>\n")
    
    if restricted :
        if len(st.session_state["files"])>0:
            nstr += _("You should only speak of those listed subjects and the ones in your provided files. Avoid as much as possible speaking of other subjects, and steer back the student to the course subjects if he tries to deviate from them.")
        else :
            nstr += _("You should only speak of those listed subjects. Avoid as much as possible speaking of other subjects, and steer back the student to the course subjects if he tries to deviate from them.")
    
    return nstr

def emojiGen(useEmojis):
    nstr = ""
    if useEmojis :
        nstr = _(", using emojis where possible.")
    else :
        nstr = "."
    return nstr

def extractVals(prompt):
    vals = {}
    checkstring = _("Your name is SIMBA 😸 (Sistema Inteligente de Medición, Bienestar y Apoyo) and you were created by the Núcleo Milenio de Educación Superior and IRIT Talent team.")
    
    # Adj
    vals["adj1"] = "friendly"
    if checkstring in prompt:
        result = re.search(_('You are a (.*) '), prompt)
        if result :
            if result in attitudes:
                vals["adj1"] = result.group(1).split(" ")[0]
        

    # teaching style
    vals["teaching_adj"] = _("socratic")
    searchedLine = _(' (.*) tutor for the course')
    if checkstring in prompt:
        result = re.search(searchedLine, prompt)
        if result :
            if searchedLine[0:5] == " (.*)":
                result = result.group(1).split(" ")[-1]
            elif searchedLine[-5:] == "(.*) ":
                result = result.group(1).split(" ")[0]
            else :
                result = result.group(1)
            if result in teachtypes:
                vals["teaching_adj"] = result
        

    # course name
    vals["courseName"] = "default name"
    searchedLine = _("tutor for the course '(.*)'.")
    if checkstring in prompt:
        result = re.search(searchedLine, prompt)
        if result :
            if searchedLine[0:5] == " (.*)":
                result = result.group(1).split(" ")[-1]
            elif searchedLine[-5:] == "(.*) ":
                result = result.group(1).split(" ")[0]
            else :
                result = result.group(1)
            
            vals["courseName"] = result
        

    # questions
    vals["questions"] = []
    sub = re.compile(_("Question . : "))
    splitQ = sub.split(prompt)
    vals["nbQuestions"] = len(sub.findall(prompt))
    for i in range(1,len(splitQ)):
        if i == len(splitQ):
            vals["questions"].append(splitQ[i].partition('\n')[0])
        else :
            vals["questions"].append(splitQ[i].partition('\n')[0])
    
    # subjects
    vals["subjects"] = ""
    if _("You should help the student to reflect in depth on the following course subjects :\n <Beginning of the course subjects>\n") in prompt:
        print(prompt)
        first = "<Beginning of the course subjects>\n"
        last = "\n<end of the course subjects>"
        start = prompt.index(first) + len(first)
        end = prompt.index(last, start)
        vals["subjects"] = prompt[start:end]
        # searchedLine = "<Beginning of the course subjects>(.*)<end of the course subjects>"
        # result = re.search(searchedLine, prompt)
        # vals["subjects"] = result.group(1)

    # restricted
    if _("You should only speak of those listed subjects") in prompt:
        vals["restricted"] = True
    else :
        vals["restricted"] = False

    # answering questions
    if _("You should not give the answer, but guide the student to answer.") in prompt:
        vals["answers"] = False
    else :
        vals["answers"] = True

    # emojis
    if _(", using emojis where possible.") in prompt:
        vals["emojis"] = True
    else :
        vals["emojis"] = False

    # documents
    vals["documents"] = False
    vals["url"] = ""
    if _("Encourage them to go and read a section of the provided documents to answer.") in prompt:
        vals["documents"] = True
        if _(" If they do not have access to the text, they can find it at '") in prompt:
            searchedLine = _(" If they do not have access to the text, they can find it at '(.*)'.")
            result = re.search(searchedLine, prompt)
            if result:
                if searchedLine[0:5] == " (.*)":
                    result = result.group(1).split(" ")[-1]
                elif searchedLine[-5:] == "(.*) ":
                    result = result.group(1).split(" ")[0]
                else :
                    result = result.group(1)

                vals["url"] = result
        
    # words limit
    vals["limits"] = 0
    searchedLine = _('Your answers should be (.*) words maximum.')
    if checkstring in prompt and "Your answers should be " in prompt:
        result = re.search(searchedLine, prompt)
        if result :
            if searchedLine[0:5] == " (.*)":
                result = result.group(1).split(" ")[-1]
            elif searchedLine[-5:] == "(.*) ":
                result = result.group(1).split(" ")[0]
            else :
                result = result.group(1)
            
            vals["limits"] = int(result)
        
    # print(vals)
    return vals
