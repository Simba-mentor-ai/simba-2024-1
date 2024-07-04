import gettext

_ = gettext.gettext

languages = ["english 🇬🇧","español 🇪🇸","français 🇫🇷"]
langSymbols = ["en","es","fr"]
langCorrespondance = {"english 🇬🇧" : "en", "español 🇪🇸" : "es", "français 🇫🇷" : "fr"}

attitudes = [_("friendly"),_("informal"),_("formal")]
teachtypes = [_("socratic"),_("other")]



accepted_extensions = [".c",".cs",".cpp",".doc",".docx",".html",".java",".json",".md",".pdf",".php",".pptx",".py",".rb",".tex",".txt",".css",".js",".sh",".ts"]