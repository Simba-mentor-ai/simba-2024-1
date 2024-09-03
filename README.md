# SIMBA-2024-1

Implementation of SIMBA, an educational chatbot meant to support students' learning strategies. This implementation was developed in collaboration with Chile's Millenium Nucleus of Higher Education (NMEdSup).
 
# Overview

The project is developped in python with streamlit, the requirements can be installed with
```bash
pip install -r requirements.txt
```
it can then be launched locally with 
```bash
streamlit run SIMBA.py
```
All the project data is hosted on a firestore database. Multiples versions of the project are hosted on streamlit.io for remote usage :
https://simba-tutor.streamlit.app/ is the stable version (based on the main branch of this git)
https://simba-test.streamlit.app/ is the test version (based on the test branch)
https://simba-aied.streamlit.app/ is a legacy version presented at the AIED workshop (based on the AIED branch)

# Project files

Here is a breakdown of the content of the files and folders :

## root folder 

### SIMBA.py 
    the main page of the application, and its entry point. it includes a short description of SIMBA and the language selection menu. If this page is accessed via an activity access link, the linked activity will be added to the logged in user's activities.

### authentication.py 
    manages the user authentication and its components (login page, user registration page, password and username retrieval). This is mainly done via "streamlit_authenticator". It's main function is "authenticate", which manages the whole authentication process. Ideally, each page of the application should start with :
    ```python
    #checking if the user is already identified
    if "authentication_status" not in st.session_state or st.session_state["authentication_status"]==False:
        authenticate()
    else :
        #rest of the page
    ```
    to ensure the user is authentified and did not access the page via an unconventional mean.
    This file uses emails.py to send password and username retrieval information to the users.

### chatbot_eval 
    Evaluation of the LLM model, mainly via trulens_eval. The data generated here can then be used to warn the user of potential faillings or just monitor its general performance. this is still a work in progress

### chatbot_helper 
    The part loading the user's chat and retrieving his threads when he enters any activity.

### chatpage_template
    This file is responsible for displaying the front end of the chat page for any activity, most of its used functions are found in chatbot_helper.py

### database_manager
    Regroups all the functions interacting with the firestore database. Many elements call its functions.

### edit_functions
    All the functions pertaining to the activities edition. Most of the functions called by "Edit_activities" are here.

### emails
    Manages the automated sending of emails for password and username recovery.

### new_edit_template
    Main component for the front end of activities creation and edition, uses a lot of the functions in edit_functions

### options
    Contains some constants for activities (all the possible teaching types, tones etc...) and the translation function.

### retriever
    Document information retriever, for use in chatbot_eval, work in progress.

### sidebar_loading
    Manages the displaying and hiding of the sidebar menus. Uses "st_pages" to avoid having to add emojis to python files names. (see original streamlit documentation about sidebar pages)

### streamlit_config_helper
    Contains the streamlit pages configuration, to be used for each page. Responsible for the pages visual aspects.

### traces_helper
    Manages the collection and sending of users traces to the firestore database.

## sidebar
    This folder contains all the pages that are not the main one (SIMBA.py)

### Admin
    Some admin functions, not displayed on the deployed versions. Enable it locally and run a local version to be certain no one else can access it.

### Edit_activities
    Activities edition page, uses new_edit_template and edit_functions. A user can obtain his activities access link here. Only accessible for teachers.

### Manage_account
    Page allowing the user to change his password or other informations. Uses streamlit_auth. Accessible for teachers and students.

### My_activities
    Page for accessing chats of the user's activities. Accessible for teachers and students.

### New_activity
    Page for creating a new activity. Accessible only to teachers.

## Locales
    contains the translations files. The internationalization of the app is managet via gettext, a detailed tutorial can be found here : https://phrase.com/blog/posts/translate-python-gnu-gettext/
    the translation file for a language must be stored in locales/[language code]/LC_MESSAGES/base.md. .po files are natural language translation files that need to be compiled with gettext or another tool like easypo or poedit.

## Contexts
    Examples of context files for app tests. Those are mainly spanish language education texts.

## .streamlit
    Contains the secrets.toml file that is NOT to be included in this git, as it contains the API keys necessary to make this app function.