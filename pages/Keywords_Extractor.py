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
st.sidebar.header("Keyword Extractor")
st.title('Keyword Extractor')

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
    #load_dotenv()
    azure_ad_token = st.secrets.TOKEN_OPENAI_GPT4

    llm_4 = AzureChatOpenAI(
        deployment_name="poc-aar-sgdy-gpt4-turbo",
        temperature=0,
        openai_api_version="2024-02-15-preview",
        azure_endpoint="https://poc-aar-sgdy.openai.azure.com/",
        openai_api_key=azure_ad_token #gitleaks:allow
    )

    keywords_prompt = PromptTemplate.from_template(KEYWORDS_TEMPLATE)
    keywords_chain_4 = keywords_prompt | llm_4

    res = keywords_chain_4.invoke({"content": text})
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
                metadata_category = bloc["meta"]["targets"]["category"] 
                if metadata_category is None:
                    continue
                metadata_url = bloc["meta"]["url"]
                titre = question["question"]
                answers = question["answer"]
                text = metadata_title + ' : ' + titre + ' ' + answers
                docs.append(Document(text = text, metadata = {"category": metadata_category, "title": metadata_title, "subtitle": titre, "url": metadata_url}))               
        return docs
    
#load documents
file_path = "source/enriched_articles_05.json"
loader = JSONLoader(file_path = file_path)
data_sample = loader.load()


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
