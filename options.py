import gettext
import streamlit as st
import database_manager as dbm

_ = gettext.gettext

def translate(basefunc):
    func = basefunc
    
    if "language" not in st.session_state:
        if "username" not in st.session_state:
            st.session_state["language"] = "en"
        else :
            st.session_state["language"] = dbm.getLanguage(st.session_state["username"])

    if st.session_state["language"] != "en" :
        if st.session_state["language"] in langSymbols:
            localizator = gettext.translation('base', localedir='locales', languages=[st.session_state["language"]])
            localizator.install()
        _ = localizator.gettext 
        func = _
    
    else :
        func = gettext.gettext

    return func

def selectLanguage() :
    if "language" not in st.session_state:
        if "username" in st.session_state:
            selected = dbm.getLanguage(st.session_state["username"])
            st.session_state["language"] = langCorrespondance[selected]
        else : 
            selected = languages[0]
            st.session_state["language"] = langSymbols[0]

    if "SelectedLanguage" in st.session_state and st.session_state["SelectedLanguage"] :
        selected = st.session_state["SelectedLanguage"]
        if langCorrespondance[selected] != st.session_state["language"]:
            st.session_state["language"] = langCorrespondance[selected]
            if "username" in st.session_state and st.session_state["username"] and st.session_state["username"] != "":
                dbm.setLanguage(st.session_state["username"],langCorrespondance[selected])
            st.rerun()  

def languageSelector():
    _ = gettext.gettext
    _ = translate(_)
    lang,stuff = st.columns([0.15,0.85])
    with lang:
        st.selectbox(_("Language"), options=languages, on_change=selectLanguage(), key="SelectedLanguage", label_visibility="hidden")


languages = ["english 🇬🇧","español 🇪🇸","français 🇫🇷"]
langSymbols = ["en","es","fr"]
langCorrespondance = {"english 🇬🇧" : "en", "español 🇪🇸" : "es", "français 🇫🇷" : "fr"}
# languages = ["english 🇬🇧","español 🇪🇸"]
# langSymbols = ["en","es"]
# langCorrespondance = {"english 🇬🇧" : "en", "español 🇪🇸" : "es"}



