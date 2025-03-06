from openai import OpenAI
import streamlit as st
from langchain_core.prompts import PromptTemplate
from traces_helper import save_navigation
import edit_functions as ef
import chatbot_helper
import time
import gettext
import datetime
import options
import database_manager as dbm

_ = gettext.gettext

_ = options.translate(_)

attitudes = [_("friendly"),_("informal"),_("formal")]
teachtypes = [_("socratic"),_("other")]
accepted_extensions = [".c",".cs",".cpp",".doc",".docx",".html",".java",".json",".md",".pdf",".php",".pptx",".py",".rb",".tex",".txt",".css",".js",".sh",".ts"]
openai_client = OpenAI()


def loadTemplate(assistant):

    new = (assistant == {})

    if "initialized" not in st.session_state :
        st.session_state["initialized"] = False


    if not st.session_state["initialized"]:
        courses = dbm.getCourses(st.session_state["username"])
        if courses == []:
            courses = ["New course"]
        else:
            courses.insert(0,"New course")

        st.session_state["UserCourses"] = courses

    title = _("Create a new activity")
    if not new :
        oldprompt = assistant["instructions"]
        vals = ef.extractVals(oldprompt)
        title = _("Modify your activity")
        
    st.title(title)

    expert = False

    #Name
    name = st.text_input(_("Activity's new name"), value = "" if new else assistant["name"], placeholder = _("New name..."))

    #Course name
    selectedCourse = st.selectbox(_("Course"), st.session_state["UserCourses"], index=0 if (new or (vals["courseName"] not in st.session_state["UserCourses"])) else (st.session_state["UserCourses"].index(vals["courseName"])))

    if selectedCourse == "New course":
        writtenCourse = st.text_input(_("Enter the new course name"), value = "" if new else vals["courseName"], placeholder = _("New name..."))

    #Description
    desc = st.text_input(_("Modify the description or enter a new one"), value = "" if new else assistant["description"], placeholder = _("New description..."))
        

    expert = st.checkbox(_("Expert mode (modify the prompt directly)"))

    if expert :
        if new :
            oldprompt = ""
        else :
            oldprompt = assistant["instructions"]
        prompt = st.text_area("Enter the prompt", value=oldprompt,height=550)
    else :
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
            if st.button(_("➕ add a question")) :
                st.session_state["nbQuestions"] = st.session_state["nbQuestions"]+1
        with remove:
            if st.button(_("➖ remove a question")) and st.session_state["nbQuestions"]>1:
                st.session_state["nbQuestions"] = st.session_state["nbQuestions"]-1

        
        for i in range(1,st.session_state["nbQuestions"]+1):
            question, delete = st.columns([0.8,0.2])
            if i-1 < len(st.session_state["questions"]):
                with question :
                    q = st.text_input(_("Question {i}").format(i=i), placeholder=_("enter the question statement"), key=f"question{i}", value=st.session_state["questions"][i-1])
                    st.session_state["questions"][i-1] = q
                if st.session_state["nbQuestions"]>1:
                    with delete :
                        st.container(height=13, border=False)
                        if st.button("❌",key="del"+str(i)):
                            st.session_state["nbQuestions"]=st.session_state["nbQuestions"]-1
                            del st.session_state["questions"][i-1]
                            st.rerun()
            else :
                with question :
                    st.session_state["questions"].append("")
                    st.session_state["questions"][i-1] = st.text_input(_("Question {i}").format(i=i), placeholder=_("enter the question statement"), key=f"question{i}")
                if st.session_state["nbQuestions"]>1:
                    with delete :
                        st.container(height=13, border=False)
                        if st.button("❌"):
                            st.session_state["nbQuestions"]=st.session_state["nbQuestions"]-1
                            del st.session_state["questions"][i-1]
                            st.rerun()
        
        #prompt
        newprompt = PromptTemplate.from_template(ef.full_template)

        if new :
            advanced = st.expander(_("Advanced settings"))
        else :
            advanced = st.container()
        
        with advanced:
            st.write(_("### Activity's assistant instructions :"))

            #attitude
            attInd = 0
            if not new and vals["adj1"] in attitudes:
                attInd = attitudes.index(vals["adj1"])

            adj1 = st.selectbox(_("What attitude should the assistant have toward the students ?"), attitudes, index=0 if new else attInd)

            # course subjects and restriction of the spoken subjects
            subjects = st.text_area(_("You can list here the course or activity subjects to indicate them more precisely to the chatbot"), value="" if new else vals["subjects"])
            restricted = st.checkbox(_("Restrict the assistant to only speaking of the listed course subjects and what is in the provided documents, if provided"),  value=False if new else vals["restricted"])
            #teaching type
            # teachtype = st.selectbox(_("What should be the assistant's approach to teaching ?"), teachtypes, index=0 if new else teachtypes.index(vals["teaching_adj"]))
            teachtype = _("socratic")

            #giving answers
            giveAnswers = st.checkbox(_("The assistant should give an answer to the activity questions if the student asks for it."), value=False if new else vals["answers"])

            #using emojis
            useEmojis = st.checkbox(_("The assistant should use emojis."), value=True if new else vals["emojis"])

            #mentioning documents
            mentiondocuments = st.checkbox(_("The assistant should encourage the student to rely on the provided documents for answering."), value=False if new else vals["documents"])
            if mentiondocuments:
                url = st.text_input(_("Is there an URL where to find those documents ?"), value="" if new else vals["url"], placeholder=_("leave empty if you have no url"))
            else :
                url = ""
            
            #word limit
            limit = st.number_input(_("include a word count limit for the assistant's answers ? (0 = no limit)"), min_value=0, value=0 if new else vals["limits"])

    #Files
    if "files" not in st.session_state or not st.session_state["initialized"]:
        st.session_state["files"] = []

    vfiles = []
    st.write(_("### Activity files"))
    if not new and "file_search" in dir(assistant["tool_resources"]) and len(assistant["tool_resources"].file_search.vector_store_ids)>0:
        st.write("Current files :")

        vid = assistant["tool_resources"].file_search.vector_store_ids[0]
        vfiles = openai_client.beta.vector_stores.files.list(vid)
        for vf in vfiles :
            delete, fname = st.columns([0.05,0.95])
            file = openai_client.files.retrieve(vf.id)
            with fname :
                st.write(file.filename)
            with delete :
                if st.button("❌",key="del"+str(vf.id)):
                    fdeleteStatus = st.status(_("Deleting the file"))
                    openai_client.beta.vector_stores.files.delete(file_id=vf.id, vector_store_id=vid)
                    openai_client.files.delete(file_id=vf.id)
                    fdeleteStatus.update(label=_("Deleted!"),state="complete")
                
    else :
        st.write(_("No files have been added yet."))


    file = st.file_uploader(_("Drop files you want to add here"), type=accepted_extensions)

    if st.button(_("Upload files")):
        
        # Upload a file to OpenAI
        if file :
            if new :
                st.session_state["files"].append(file)
                st.write(_("file added, to be uploaded upon activity creation."))
            else:
                status = st.status(_("Uploading file"))
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
                    status.update(label=_("Linking file to the activity"))
                    openai_client.beta.assistants.update(assistant_id=assistant["id"],tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},)
                
                status.update(label=_("File added to the activity!"),state="complete")
                # st.session_state["assistants"] = ef.getAssistants()
                st.session_state["assistants"] = ef.getUserAssistants()
                st.session_state["UserCourses"] = dbm.getCourses(st.session_state["username"])
                assistant = st.session_state["assistants"][st.session_state["selectedID"]]

            file = None

        else :
            error(_("please, add a file to be uploaded first."))


    start, end = st.columns([.5,.5])

    oldStart = None
    oldStartBool = False
    oldEnd = None
    oldEndBool = False
    if not new :
        if "startDate" in assistant["metadata"].keys():
            oldStartBool = True
            oldStart = datetime.datetime.strptime(assistant["metadata"]["startDate"], "%Y/%m/%d")

        if "endDate" in assistant["metadata"].keys():
            oldEndBool = True
            oldEnd = datetime.datetime.strptime(assistant["metadata"]["endDate"], "%Y/%m/%d")

    with start :
        startBool = st.checkbox(_("I want the activity to be accessible only from a certain day"), value=oldStartBool)
        if startBool:
            startDate = st.date_input("start date", value=oldStart)
    
    with end :
        endBool = st.checkbox(_("I want the activity to be hidden after a certain day"), value=oldEndBool)
        if endBool:
            endDate = st.date_input("end date", value=oldEnd)

    st.session_state["initialized"] = True

    submit,cancel = st.columns([1,.2])

    if not new :
        with cancel:
            if st.button(_("Cancel")):
                st.session_state["initialized"] = False
                st.rerun()
    with submit:
        if st.button(_("Submit")):

            if selectedCourse == "New course":
                course = writtenCourse
            else :
                course = selectedCourse
            emptyquestion = False
            emptyI = 0
            for i in range(0,st.session_state["nbQuestions"]):
                if st.session_state["questions"][i] == "":
                    emptyquestion = True
                    emptyI = i
                    break

            if name == "":
                error(_("Please, give a name to your activity."))
            elif st.session_state["nbQuestions"] == 0 and not expert:
                error(_("The activity needs to have at least one question."))
            elif emptyquestion and not expert:
                error(_("The question " + str(emptyI+1) + " have no text."))

            else :
                if expert : 
                    instructions = prompt
                else :
                    instructions = newprompt.format(
                        courseName=course, 
                        teaching_adj=teachtype,
                        adj1 = adj1, 
                        emojis = ef.emojiGen(useEmojis),
                        questions = ef.questionsGen(),
                        subjects = ef.subjectsGen(subjects,restricted),
                        answers = ef.answersGen(giveAnswers),
                        teaching_type = ef.teachTypeGen(teachtype),
                        documents = ef.docsGen(mentiondocuments, url),
                        limits= ef.limitsgen(limit)
                    )
                metadata = {}
                if startBool and endBool :
                    metadata = {"startDate":startDate.strftime("%Y/%m/%d"), "endDate":endDate.strftime("%Y/%m/%d")}
                elif startBool :
                    metadata = {"startDate":startDate.strftime("%Y/%m/%d")}
                elif endBool :
                    metadata = {"endDate":endDate.strftime("%Y/%m/%d")}
                if new :
                    status = st.status(label=_("Creating activity"))
                    vector_store = None
                    if len(st.session_state["files"])>0 :
                        vector_store = openai_client.beta.vector_stores.create(name=name)
                        status.update(label = _("uploading the files"))
                    for f in st.session_state["files"] :
                        openai_client.beta.vector_stores.files.upload(
                            vector_store_id=vector_store.id, file=f
                        )
                    status.update(label=_("Creating activity"))
                    if vector_store:
                        tool_resources = {"file_search": {"vector_store_ids": [vector_store.id]}}
                    else :
                        tool_resources = {}
                    activity = openai_client.beta.assistants.create(name = name, description = desc, instructions = instructions, tools=[{"type": "file_search"}], model="gpt-4o-mini",tool_resources=tool_resources, metadata=metadata)
                    dbm.createActivity(activity,course)
                    save_navigation(activity.id, "created")
                    st.session_state["nbQuestions"] = 1
                    st.session_state["questions"] = [""]
                    st.session_state["initialized"] = False 
                    success(_("The new activity have been successfully created"))
                    

                else :
                    warning_edit(assistant,name,desc,instructions,metadata,course)
                    # openai_client.beta.assistants.update(assistant["id"], name = name, description = desc, instructions = instructions)
                    # chatbot_helper.disable_activity_threads(assistant["id"])
                    # success("The activity have been successfully updated")


@st.experimental_dialog(_("Success"))
def success(line):
    st.write(line)
    if st.button(_("ok")):
        st.session_state["assistants"] = ef.getUserAssistants()
        st.session_state["initialized"] = False   
        st.rerun() 

@st.experimental_dialog(_("Error"))
def error(line):
    st.write(line)
    if st.button(_("ok")):
        st.rerun()      

@st.experimental_dialog(_("warning"))
def warning_edit(assistant,name,desc,instructions,metadata,course):
    st.write(_("Editing this activity will reset it for all students, If students are working with the current activity, they will have to start the activity over. If you want to keep it as it is, we recommend you create a new activity"))
    cancel,ok = st.columns([1,0.5])
    with cancel :
        if st.button(_("cancel")):
            st.rerun()
    with ok :
        if st.button(_("ok")):
            status = st.status(_("Updating the activity"))
            activity = openai_client.beta.assistants.update(assistant["id"], name = name, description = desc, instructions = instructions, metadata=metadata)
            dbm.updateActivity(activity,course)
            chatbot_helper.disable_activity_threads(assistant["id"])
            status.update(label=_("Activity successfully updated!"),state='complete')
            save_navigation(assistant["id"], "updated")
            st.session_state["assistants"] = ef.getUserAssistants()
            st.session_state["nbQuestions"] = 1
            st.session_state["questions"] = [""]
            st.session_state["initialized"] = False 
            time.sleep(1)
            st.rerun()