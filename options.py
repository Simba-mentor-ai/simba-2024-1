import gettext
import streamlit as st


_ = gettext.gettext

def translate(basefunc):
    if "language" not in st.session_state:
        st.session_state["language"] = "en"
        func = basefunc

    elif st.session_state["language"] != "en" :
        print("translating", st.session_state["language"])
        localizator = gettext.translation('base', localedir='locales', languages=[st.session_state["language"]])
        localizator.install()
        _ = localizator.gettext 
        func = _

    else :
        func = basefunc

    return func

_ = translate(_)

languages = ["english 🇬🇧","español 🇪🇸","français 🇫🇷"]
langSymbols = ["en","es","fr"]
langCorrespondance = {"english 🇬🇧" : "en", "español 🇪🇸" : "es", "français 🇫🇷" : "fr"}

attitudes = [_("friendly"),_("informal"),_("formal")]
teachtypes = [_("socratic"),_("other")]



accepted_extensions = [".c",".cs",".cpp",".doc",".docx",".html",".java",".json",".md",".pdf",".php",".pptx",".py",".rb",".tex",".txt",".css",".js",".sh",".ts"]

