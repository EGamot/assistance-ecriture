from langchain.prompts import PromptTemplate
from langchain_core.prompts.chat import PromptTemplate

import streamlit as st
from source.model_settings import llm_4
from st_pages import add_page_title

# Either this or add_indentation() MUST be called on each page in your
# app to add indendation in the sidebar
add_page_title()

st.write("Le LLM vérifie la cohérence, l'orthographe du texte ainsi que le respect de la charte.")

def coherence_spelling_4(content:str) -> str:
    COHE_SPELL_TEMPLATE = """You are an assistant writer for Bouygues Telecom, a telecommunications operator in France.
    CONTEXT:
        Here are some question/answer couples that appear in an article the FAQ section of the website. These couples are designed to help customers resolving their issues regarding network, billing problems, technical problems with the mobile, technical problems with the box, etc.
    OBJECTIVE:
        You must check the spelling and the coherence of the text. Identify and correct any typos, grammatical errors, awkward phrasing, or other minor issues that may have been overlooked. 
        Beyond surface-level corrections, your role also involves polishing the text to improve its overall readability. 
        The text must respect the following charter :
          - Using suggestive forms or the second person plural: avoiding imperative formulas.
          - We invite action in a different way by suggesting and striving to be more inclusive, rather than using imperative language.
          - In the customer journey or bullet points, it is recommended to systematically use 'you' instead of 'I'. The voice of the messaging should be that of the customer.
          - Eliminate any form of negativity: keep a positive focus! Therefore it's recommended to avoid using negative words or concepts as much as possible.
          - We encourage action by making suggestions and striving to be more inclusive. We value each employee and customer by starting with the feminine form. We aim to restore balance between feminine and masculine by using more inclusive alternatives whenever possible, which also enables better text length management depending on the medium. This can include using different designations and adjectives, as well as modifying sentence structures.
          - We adopt a collective and customer-focused approach. We use 'on' when aiming for a closer relationship and more inclusive discourse, with stronger interactions. 'Nous' is used when the brand is talking about itself and the actions it takes as an entity, such as commitments, beliefs, and positioning.
          - We prioritize empathy and foster the human dimension of Bouygues Telecom. We use markers of orality in a measured way, such as 'let's go', 'here we go', 'oh yeah', 'boom', 'there you go', 'well', 'ah', 'oh', 'hey' (and others), to create a more personal and engaging tone. We show respect by always using grammatically correct and accurate language in our messages.
        If you detect a problem with the spelling, you must rewrite the sentence with the correct one and use bold text to highlight the correction.
        If you detect a problem with the coherence of the text, you must explain why.
        You must absolutely higlight your modification by using bold text !
        All text must remain in french. Your response must also be in french.
    ARTICLE:
        {content} 
    
    """ # noqa E501    
    cohe_spell_prompt = PromptTemplate.from_template(COHE_SPELL_TEMPLATE)
    cohe_spell_chain_4 = cohe_spell_prompt | llm_4
    res = cohe_spell_chain_4.invoke({"content":content})
    return res.content

default_text = "Comment assigné mon assurance à mon nouveau mobile ? Si vous avez assuré votre téléphone mobile auprès de SPB (Assurance Mobile), au moment de votre renouvellement et s'il répond à certains critères, vous aurez plusieurs possibilités. Vous pouvez adhérer à une assurance pour votre nouveau mobile sans résilier celle de votre ancien appareil (dans le cas où celui-ci serait encore utilisé) : vous aurez alors 2 assurances mobiles. Vous pouvez résilier l'assurance de votre ancien mobile : vous devez directement contacter SPB pour qu'il résilie votre contrat. Renouvellement de mobile en boutique ? Vous pouvez transférer l'assurance de votre ancien mobile sur le nouveau (ce transfert est automatiquement proposé en boutique)."
st.write('Exemple de texte :')
st.markdown(" *Comment assigné mon assurance à mon nouveau mobile ? Si vous avez assuré votre téléphone mobile auprès de SPB (Assurance Mobile), au moment de votre renouvellement et s'il répond à certains critères, vous aurez plusieurs possibilités. Vous pouvez adhérer à une assurance pour votre nouveau mobile sans résilier celle de votre ancien appareil (dans le cas où celui-ci serait encore utilisé) : vous aurez alors 2 assurances mobiles. Vous pouvez résilier l'assurance de votre ancien mobile : vous devez directement contacter SPB pour qu'il résilie votre contrat. Renouvellement de mobile en boutique ? Vous pouvez transférer l'assurance de votre ancien mobile sur le nouveau (ce transfert est automatiquement proposé en boutique).*" )
text = st.text_area('Enter your text', '', height=300)
if text != '':
    with st.spinner('Wait for it...'):
        answer = coherence_spelling_4(text)
        st.container(border=True).write(answer)