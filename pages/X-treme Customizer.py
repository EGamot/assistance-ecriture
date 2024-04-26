import json
from pathlib import Path
from typing import List, Optional, Union, Iterable, Dict, Any
from llama_index.core.schema import Document
from langchain.document_loaders.base import BaseLoader
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.prompts.chat import PromptTemplate

import streamlit as st
#from dotenv import load_dotenv
#import os

# Page title
st.sidebar.header("X-treme Customizer")
st.title('X-treme Customizer')

st.write("Sur cette page, vous pouvez appliquer le prompt de votre choix sur un article.")
st.write("Dans un premier temps, vous copiez l'URL de la page de votre choix. Le titre de l'article s'affiche à l'écran. Puis vous pouvez entrer les instructions pour le LLM et enfin sélectionner la partie du texte sur laquelle les instructions doivent être appliquées.")

def custom(instruction:str, content:str) -> str:
    CUSTOM_TEMPLATE = """You are an assistant writer for Bouygues Telecom, a telecommunications operator in France.
    CONTEXT:
        Here if an extract from an article in the FAQ section of the website. This article is designed to help customers resolving their issues regarding network, billing problems, technical problems with the mobile, technical problems with the box, etc.
    OBJECTIVE:
        {instruction}
        All text must remain in french.
    ARTICLE:
        {content} 
    
    """ # noqa E501
    #load_dotenv()
    azure_ad_token = st.secrets.TOKEN_OPENAI_GPT4
    llm_4 = AzureChatOpenAI(
        deployment_name="poc-aar-sgdy-gpt4-turbo",
        temperature=0,
        openai_api_version="2024-02-15-preview",
        azure_endpoint="https://poc-aar-sgdy.openai.azure.com/",
        openai_api_key=azure_ad_token)#gitleaks:allow
    
    custom_prompt = PromptTemplate.from_template(CUSTOM_TEMPLATE)
    custom_chain = custom_prompt | llm_4
    res = custom_chain.invoke({"content":content, "instruction":instruction})
    return res.content


class JSONLoader(BaseLoader):
    def __init__(
        self,
        file_path: Union[str, Path],
        content_key: Optional[str] = None,
        ):
        self.file_path = Path(file_path).resolve()
        self._content_key = content_key
    def load(self) -> List[Document]:
        """Load and return documents from the JSON file."""
        docs = []
        # Load JSON file
        with open(self.file_path, encoding='utf-8') as file:
            data = json.load(file)
        for bloc in data: 
            for question in bloc["content"]["enriched"]:
                metadata_title = bloc["meta"]["title"]
                metadata_url = bloc["meta"]["url"]
                metadata_summary = bloc["meta"]["summary"]
                titre = question["question"]
                answers = question["answer"]
                text = titre + ' ' + answers
                docs.append(Document(text = text, metadata = {"title": metadata_title, "summary": metadata_summary, "subtitle": titre, "url": metadata_url}))               
        return docs
    
#load documents
file_path = "source/enriched_articles_05.json"
loader = JSONLoader(file_path = file_path)
data_sample = loader.load()

url = st.text_area('Enter your url', '', height=50)

if url!= '':
    chunks = [chunk for chunk in data_sample if chunk.metadata['url'] == url]
    titre = chunks[0].metadata['title']
    summary = chunks[0].metadata['summary']

    st.container(border = True).write(titre)

    instruction = st.text_area('Ecrivez vos instructions :', '', height=400)

    if instruction != '':
        extract = st.selectbox(
            "Sur quelle partie de l'article souhaitez-vous appliquer le LLM ?",
            ('Tout le contenu, titre et résumé inclus', 'Le titre', 'Le résumé', 'Les questions/réponses', "Résumé et questions/réponses")
        )
        
        if st.button('Go !'):
            with st.spinner("Wait for it..."):
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
                answer = custom(content, instruction)

            st.write(answer)
