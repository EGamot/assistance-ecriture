from langchain.prompts import PromptTemplate
from langchain_core.prompts.chat import PromptTemplate

import streamlit as st
from source.model_settings import llm_4
from source.knowledge_load import data_sample
from st_pages import add_page_title

# Either this or add_indentation() MUST be called on each page in your
# app to add indendation in the sidebar
add_page_title()

st.write('Sur cette page, vous pouvez appliquer le prompt de votre choix sur un article.')

st.markdown("""
            1. Copiez l'URL de la page de votre choix : le titre de l'article s'affiche à l'écran.  
            2. Sélectionnez la partie du texte sur laquelle les instructions doivent être appliquées : titre, contenu, résumé, etc...  
            3. Entrez les instructions pour le LLM, comme par exemple : 'Recopie le texte en mettant les mots-clés en gras', 'Propose une réécriture de ce texte avec un ton plus détendu', etc... 
            4. Cliquez sur le bouton 'Go !' et c'est parti ! """)

st.write('')

def custom(instruction:str, content:str) -> str:
    CUSTOM_TEMPLATE = """You are an assistant writer for Bouygues Telecom, a telecommunications operator in France.
    CONTEXT:
        Here if an extract from an article in the FAQ section of the website. This article is designed to help customers resolving their issues regarding network, billing problems, technical problems with the mobile, technical problems with the box, etc.
    OBJECTIVE:
        You must apply this instruction on the extract ONLY : {instruction}
    GUIDELINES:
        All text must remain in french and respect the following charter :
        - Using suggestive forms or the second person plural: avoiding imperative formulas.
        - We invite action in a different way by suggesting and striving to be more inclusive, rather than using imperative language.
        - In the customer journey or bullet points, it is recommended to systematically use 'you' instead of 'I'. The voice of the messaging should be that of the customer.
        - Eliminate any form of negativity: keep a positive focus! Therefore it's recommended to avoid using negative words or concepts as much as possible.
        - We encourage action by making suggestions and striving to be more inclusive. We value each employee and customer by starting with the feminine form. We aim to restore balance between feminine and masculine by using more inclusive alternatives whenever possible, which also enables better text length management depending on the medium. This can include using different designations and adjectives, as well as modifying sentence structures.
        - We adopt a collective and customer-focused approach. We use 'on' when aiming for a closer relationship and more inclusive discourse, with stronger interactions. 'Nous' is used when the brand is talking about itself and the actions it takes as an entity, such as commitments, beliefs, and positioning.
        - We prioritize empathy and foster the human dimension of Bouygues Telecom. We use markers of orality in a measured way, such as 'let's go', 'here we go', 'oh yeah', 'boom', 'there you go', 'well', 'ah', 'oh', 'hey' (and others), to create a more personal and engaging tone. We show respect by always using grammatically correct and accurate language in our messages.
    EXTRACT:
        {content} 
    
    """ # noqa E501
    custom_prompt = PromptTemplate.from_template(CUSTOM_TEMPLATE)
    custom_chain = custom_prompt | llm_4
    res = custom_chain.invoke({"content":content, "instruction":instruction})
    return res.content

url = st.text_area('Enter your url', '', height=50)

if url != '':
    chunks = [chunk for chunk in data_sample if chunk.metadata['url'] == url]
    titre = chunks[0].metadata['title']
    summary = chunks[0].metadata['summary']

    st.container(border = True).write(titre)

    extract = st.selectbox(
            "Sur quelle partie de l'article souhaitez-vous appliquer le LLM ?",
            ('Tout le contenu, titre et résumé inclus', 'Le titre', 'Le résumé', 'Les questions/réponses', "Résumé et questions/réponses")
        )
    if extract == 'Tout le contenu, titre et résumé inclus':
        content = [titre] + [summary] + [chunk.text for chunk in chunks]
    elif extract == 'Le titre':
        content = titre
    elif extract == 'Le résumé':
        content = summary
    elif extract == 'Les questions/réponses':
        content = chunks
    elif extract == "Résumé et questions/réponses":
        content = [summary] + chunks

    instruction = st.text_area('Ecrivez vos instructions :', '', height=400)

    if st.button('Go !'):
        if instruction != '' :
            with st.spinner("Wait for it..."):
                answer = custom(content, instruction)
            st.write(answer)
        else :
            st.write("Il faut entrer des instructions !")