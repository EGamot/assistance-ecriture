from langchain.prompts import PromptTemplate
from langchain_core.prompts.chat import PromptTemplate

import streamlit as st
from source.model_settings import llm_4
from st_pages import add_page_title

# Either this or add_indentation() MUST be called on each page in your
# app to add indendation in the sidebar
add_page_title()

st.write("A partir d'un sujet donné et du briefing correspondant, le LLM va proposer un article respectant la charte d'écriture ainsi que la structure des articles de FAQ.")

# Text input
topic = st.text_area("Quel est le sujet de l'article ?", '', height=100)
brief = st.text_area('Quel est le briefing pour cet article ?', '', height=300)


def writing_new_content_4(topic:str, content:str) -> str:
    WRITING_TEMPLATE = """
    CONTEXT:
        You are an assistant writer for Bouygues Telecom, a telecommunications operator in France.

    OBJECTIVE:
        You must write an article for the FAQ section of the website about this topic : {topic}
        The article must contains :
            - a title
            - a brief summary
            - an URL beginning with 'https://www.assistance.bouyguestelecom.fr/s/article/' and followed by three or four key-words, without accent, without acronym, separated by hyphens ;
            - a content divided in several paragraph 
            - each paragraph must begin by a question in bold format (the question must be user-friendly) and there must be a carriage return between the question and the answer. 
    
    GUIDELINES:
        The text must respect the following charter :
            - Using suggestive forms or the second person plural: avoiding imperative formulas.
            - We invite action in a different way by suggesting and striving to be more inclusive, rather than using imperative language.
            - In the customer journey or bullet points, it is recommended to systematically use 'you' instead of 'I'. The voice of the messaging should be that of the customer.
            - Eliminate any form of negativity: keep a positive focus! Therefore it's recommended to avoid using negative words or concepts as much as possible.
            - We encourage action by making suggestions and striving to be more inclusive. We value each employee and customer by starting with the feminine form. We aim to restore balance between feminine and masculine by using more inclusive alternatives whenever possible, which also enables better text length management depending on the medium. This can include using different designations and adjectives, as well as modifying sentence structures.
            - We adopt a collective and customer-focused approach. We use 'on' when aiming for a closer relationship and more inclusive discourse, with stronger interactions. 'Nous' is used when the brand is talking about itself and the actions it takes as an entity, such as commitments, beliefs, and positioning.
            - We prioritize empathy and foster the human dimension of Bouygues Telecom. We use markers of orality in a measured way, such as 'let's go', 'here we go', 'oh yeah', 'boom', 'there you go', 'well', 'ah', 'oh', 'hey' (and others), to create a more personal and engaging tone. We show respect by always using grammatically correct and accurate language in our messages.
    
        Here are some additional instructions :
        {content} 

        All text must remain in french. Your response must also be in french.

    """ # noqa E501
    writing_prompt = PromptTemplate.from_template(WRITING_TEMPLATE)
    writing_chain = writing_prompt | llm_4
    res = writing_chain.invoke({"topic": topic, "content": content})
    return res.content

if st.button('Go !'):
    if topic != '' and brief != '':
        with st.spinner('Wait for it...'):
            answer = writing_new_content_4(topic = topic, content = brief)
            st.container(border=True).write(answer)
    else:
        st.container(border=True).write("il faut remplir tous les champs !")

#if text != '':
#    with st.spinner('Wait for it...'):
#        answer = coherence_spelling_4(text)
#        st.container(border=True).write(answer)