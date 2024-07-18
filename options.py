import gettext
import streamlit as st


_ = gettext.gettext

def translate():
    if "language" not in st.session_state:
        st.session_state["language"] = "en"

    elif st.session_state["language"] != "en" :
        localizator = gettext.translation('base', localedir='locales', languages=[st.session_state["language"]])
        localizator.install()
        _ = localizator.gettext 

translate()

languages = ["english 🇬🇧","español 🇪🇸","français 🇫🇷"]
langSymbols = ["en","es","fr"]
langCorrespondance = {"english 🇬🇧" : "en", "español 🇪🇸" : "es", "français 🇫🇷" : "fr"}

attitudes = [_("friendly"),_("informal"),_("formal")]
teachtypes = [_("socratic"),_("other")]



accepted_extensions = [".c",".cs",".cpp",".doc",".docx",".html",".java",".json",".md",".pdf",".php",".pptx",".py",".rb",".tex",".txt",".css",".js",".sh",".ts"]

