from langchain.prompts import PromptTemplate
from langchain_core.prompts.chat import PromptTemplate

import streamlit as st
from source.model_settings import llm_4
from source.knowledge_load import data_sample
from st_pages import add_page_title

# Either this or add_indentation() MUST be called on each page in your
# app to add indendation in the sidebar
add_page_title()

st.write("A partir de l'URL d'un article, le LLM récupère tout le contenu question/réponse correspondant. A partir de ce contenu, il propose un titre pour l'article ainsi qu'un bref résumé en guise d'introduction.")

type = st.radio("Je veux appliquer sur :",
         ["un texte", "une page"])

def summary_4(content:str) -> str:
    SUMMARY_TEMPLATE = """You are an assistant writer for Bouygues Telecom, a telecommunications operator in France.
    CONTEXT:
        Here are some question/answer couples that appear in an article the FaQ section of the website. These couples are designed to help customers resolving their issues regarding network, billing problems, technical problems with the mobile, technical problems with the box, etc.
    OBJECTIVE:
        You must then provide a title for this article and a brief summary as introduction.
        All text must remain in french.
    GUIDELINES:
       The text must respect the following charter :
          - Using suggestive forms or the second person plural: avoiding imperative formulas.
          - We invite action in a different way by suggesting and striving to be more inclusive, rather than using imperative language.
          - In the customer journey or bullet points, it is recommended to systematically use 'you' instead of 'I'. The voice of the messaging should be that of the customer.
          - Eliminate any form of negativity: keep a positive focus! Therefore it's recommended to avoid using negative words or concepts as much as possible.
          - We encourage action by making suggestions and striving to be more inclusive. We value each employee and customer by starting with the feminine form. We aim to restore balance between feminine and masculine by using more inclusive alternatives whenever possible, which also enables better text length management depending on the medium. This can include using different designations and adjectives, as well as modifying sentence structures.
          - We adopt a collective and customer-focused approach. We use 'on' when aiming for a closer relationship and more inclusive discourse, with stronger interactions. 'Nous' is used when the brand is talking about itself and the actions it takes as an entity, such as commitments, beliefs, and positioning.
          - We prioritize empathy and foster the human dimension of Bouygues Telecom. We use markers of orality in a measured way, such as 'let's go', 'here we go', 'oh yeah', 'boom', 'there you go', 'well', 'ah', 'oh', 'hey' (and others), to create a more personal and engaging tone. We show respect by always using grammatically correct and accurate language in our messages.
    ARTICLE:
        {content} 
    
    """ # noqa E501
    summary_prompt = PromptTemplate.from_template(SUMMARY_TEMPLATE)
    summary_chain_4 = summary_prompt | llm_4
    res = summary_chain_4.invoke({"content":content})
    return res.content

if type == "une page":
    link = st.text_area("Entrez l'URL", '', height=50)

    if link != '':
        chunks = [chunk.text for chunk in data_sample if chunk.metadata['url'] == link]
        old_title = [chunk for chunk in data_sample if chunk.metadata['url'] == link][0].metadata['title']
        st.container(border=True).write(old_title)
        with st.spinner('Wait for it...'):
            st.write(summary_4(chunks))
if type == "un texte":
    text = st.text_area("Entrez le texte à résumer", '', height = 500)
    if text != '':
        with st.spinner('Wait for it...'):
            st.write(summary_4(text))