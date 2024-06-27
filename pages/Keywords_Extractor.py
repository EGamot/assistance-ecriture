from langchain.prompts import PromptTemplate
from langchain_core.prompts.chat import PromptTemplate

import streamlit as st
from source.model_settings import llm_4
from source.knowledge_load import data_sample
from st_pages import add_page_title

# Either this or add_indentation() MUST be called on each page in your
# app to add indendation in the sidebar
add_page_title()

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()

st.write("A partir de l'URL d'un article, le LLM extrait trois mots-clés pour chacun des couples question/réponse de la page.")

def progressbar(value):
    if value <= 0.25 :
        text = "Patience..."
    elif value > 0.25 and value <0.75:
        text = "Oui oui, c'est un peu long..."
    else:
        text = "Courage, on y est presque !!"
    return text

def key_4(text: str) -> dict:
    """ Generate a new phrase according to the user query.
    Args:
        query (str): user query
    Returns:
        dict: rephrase, tokens
    """
    KEYWORDS_TEMPLATE = """You are an assistant for Bouygues Telecom, a telecommunications operator in France.
    CONTEXT:
        Here is a question/answer couple extracted from an article in the FAQ section of the website. The article is designed to help customers resolving their issues regarding network, billing problems, technical problems with the mobile, technical problems with the box, etc.
    OBJECTIVE:
        You must extract a list of three keywords from the question/answer couple that will identifying the content of the text with a query search. 
        Each keyword must be in french, contain THREE words MAX  and must be separated by commas, for example : numéro RIO, suivi incident, suivi de commande.
        Each keyword MUST be SINGULAR.
    TEXT : 
        {content}
    """ # noqa E501

    keywords_prompt = PromptTemplate.from_template(KEYWORDS_TEMPLATE)
    keywords_chain_4 = keywords_prompt | llm_4

    res = keywords_chain_4.invoke({"content": text})
    return res.content

# Text input
url = st.text_area('Enter your url', '', height=50)

chunks = [chunk for chunk in data_sample if chunk.metadata['url'] == url]
nb = len(chunks)
if url != '':
    for i, chunk in enumerate(chunks) :
        st.write(chunk.metadata['subtitle'])
        with st.spinner('Wait for it...'):
            st.markdown("*Keywords :* ")
            st.container(border=True).write(key_4(chunk.text).replace(","," / "))
            st.divider()
        progress_bar.progress((i+1)/nb, progressbar((i+1)/nb))
    progress_bar.progress(100, "Ouf, terminé !")