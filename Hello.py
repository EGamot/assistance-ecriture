import streamlit as st
from st_pages import Page, Section, add_page_title, show_pages

st.set_page_config(page_title="Hello")

# Either this or add_indentation() MUST be called on each page in your
# app to add indendation in the sidebar
add_page_title()

show_pages(
    [
        Page("Hello.py", "Welcome", "🏠"),
        # Can use :<icon-name>: or the actual icon

        Section(name="Recherche"),
        Page("pages/Page_Retriever.py", "Rechercher dans la FAQ"),
        # Since this is a Section, all the pages underneath it will be indented
        # The section itself will look like a normal page, but it won't be clickable

        Section(name="Vérification du texte"),
        # The pages appear in the order you pass them
        Page("pages/Summary_Assistant.py", "Génération de résumé et titre"),
        Page("pages/Judge_Title.py", "Vérification des sous-titres"),
        Page("pages/Spelling_Checker.py", "Vérification du contenu (syntaxe, cohérence, charte, ...)"),
        Page("pages/All_in_one.py", "Tout-en-un"),
        Page("pages/X-treme Customizer.py", "Prompt personnalisé"),
        
        Section(name="Aide à l'écriture"),
        Page("pages/Nouvel_Article.py", "Ecriture d'un nouvel article"),
        
        Section(name="Autre"),
        Page("pages/Keywords_Extractor.py", "Extraction des mots-clés"),
    ]
)

st.title("to the RewrAITer")

st.image("rewrite.jpg")