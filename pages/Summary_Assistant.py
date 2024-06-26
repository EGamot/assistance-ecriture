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
st.sidebar.header("Summary Assistant")
st.title('Summary Assistant')

st.write("A partir de l'URL d'un article, le LLM récupère tout le contenu question/réponse correspondant. A partir de ce contenu, il propose un titre pour l'article ainsi qu'un bref résumé en guise d'introduction.")

def summary_4(content:str) -> str:
    SUMMARY_TEMPLATE = """You are an assistant writer for Bouygues Telecom, a telecommunications operator in France.
    CONTEXT:
        Here are some question/answer couples that appear in an article the FaQ section of the website. These couples are designed to help customers resolving their issues regarding network, billing problems, technical problems with the mobile, technical problems with the box, etc.
    OBJECTIVE:
        You must provide a title for this article and a brief summary as introduction.
    GUIDELINES:
        All text must remain in french and respect the following charter :
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
    #load_dotenv()
    azure_ad_token = st.secrets.TOKEN_OPENAI_GPT4
    llm_4 = AzureChatOpenAI(
        deployment_name="poc-aar-sgdy-gpt4-turbo",
        temperature=0,
        openai_api_version="2024-02-15-preview",
        azure_endpoint="https://poc-aar-sgdy.openai.azure.com/",
        openai_api_key=azure_ad_token)#gitleaks:allow
    
    summary_prompt = PromptTemplate.from_template(SUMMARY_TEMPLATE)
    summary_chain_4 = summary_prompt | llm_4
    res = summary_chain_4.invoke({"content":content})
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
                metadata_link = bloc["meta"]["url"]
                titre = question["question"]
                answers = question["answer"]
                text = titre + ' ' + answers
                docs.append(Document(text = text, metadata = {"title": metadata_title, "subtitle": titre, "link": metadata_link}))               
        return docs
    
#load documents
file_path = "source/enriched_articles_05.json"
loader = JSONLoader(file_path = file_path)
data_sample = loader.load()

# Text input
link = st.text_area('Enter your url', '', height=50)

if link != '':
    chunks = [chunk.text for chunk in data_sample if chunk.metadata['link'] == link]
    old_title = [chunk for chunk in data_sample if chunk.metadata['link'] == link][0].metadata['title']
    st.container(border=True).write(old_title)
    with st.spinner('Wait for it...'):
        st.write(summary_4(chunks))
