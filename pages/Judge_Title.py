import json
from pathlib import Path
from typing import List, Optional, Union
from llama_index.core.schema import Document
from langchain.document_loaders.base import BaseLoader
from langchain_openai import AzureChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.prompts.chat import PromptTemplate

import streamlit as st
#from dotenv import load_dotenv
#import os
import re

# Page title
st.sidebar.header("Judge Title")
st.title('Judge Title')

progress_bar = st.sidebar.progress(0)

st.write("A partir de l'URL d'un article, le LLM évalue la cohérence et l'aspect user-friendly de chacun des titres-questions par rapport au contenu du paragraphe correspondant.")
st.write("Si la question ne lui paraît pas pertinente par rapport au texte, il en suggère d'autres.")

type = st.radio("Je veux appliquer sur :",
         ["un texte", "une page"])

def progressbar(value):
    if value <= 0.25 :
        text = "Patience..."
    elif value > 0.25 and value <0.75:
        text = "Oui oui, c'est un peu long..."
    else:
        text = "Courage, on y est presque !!"
    return text

def title_4(title: str, question: str, answer: str) -> str:
    """ Generate a new phrase according to the user query.
    Args:
        query (str): user query
    Returns:
        dict: rephrase, tokens
    """
    TITLE_TEMPLATE = """You are an assistant writer for Bouygues Telecom, a telecommunications operator in France.
    CONTEXT:
        Here is a paragraph extracted from an article in the FAQ section of the Bouygues Telecom website. The title of the article is {title}
        The paragraph has a title, which is expressed as a question.
    
    OBJECTIVE:
         You must judge if the question is befitting the following text. The question must be explicit, related to the content of the text and give some context about it. 
         The question must also reflect an issue that could be encoutered by a user : it must look like a query search initiated by a user.
         You must score the consistency of the question using one of these three words :
         - appropriate : the question is perfectly appropriate to the content
         - mixed : the question doesn't fit exactly the content, the context being slightly different, or the question isn't user-friendly
         - inappropriate : the question doesn't fit the content
        The score must appear between brackets : [appropriate], [mixed] or [inappropriate].
        Your must then explain your scoring, in french.
        If the is [mixed] or [inappropriate], you must suggest three other questions, formulated in french.

    Question : {question}
    Text :  {answer} 
    
    """ # noqa E501
    load_dotenv()
    azure_ad_token = os.getenv('TOKEN_OPENAI_GPT4')
    llm_4 = AzureChatOpenAI(
        deployment_name="poc-aar-sgdy-gpt4-turbo",
        temperature=0,
        openai_api_version="2024-02-15-preview",
        azure_endpoint="https://poc-aar-sgdy.openai.azure.com/",
        openai_api_key=azure_ad_token) #gitleaks:allow
    
    title_prompt = PromptTemplate.from_template(TITLE_TEMPLATE)
    title_chain_4 = title_prompt | llm_4
    res = title_chain_4.invoke({"title" : title, "question": question, "answer":answer})
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
                docs.append(Document(text = answers, metadata = {"category": metadata_category, "title": metadata_title, "subtitle": titre, "url": metadata_url}))               
        return docs
    
#load documents
file_path = r"source/enriched_articles_05.json"
loader = JSONLoader(file_path = file_path)
data_sample = loader.load()

if type == "une page":
# Text input
    url = st.text_area("Entrez l'URL de la page", '', height=50)
    if url != '':
        chunks = [chunk for chunk in data_sample if chunk.metadata['url'] == url]
        nb = len(chunks)
        for i,chunk in enumerate(chunks) :
            st.write(chunk.metadata['subtitle'])
            with st.spinner('Wait for it...'):
                response = title_4(title = chunk.metadata['title'], question = chunk.metadata['subtitle'], answer = chunk.text)
                tag = re.findall(r'\[(.*)\]', response)
                explanation = re.sub(r'\[.*\]', '', response)
                if tag[0] == 'appropriate':
                    st.markdown(''' :green[APPROPRIATE]''')
                    st.write(explanation)
                elif tag[0] == 'mixed':
                    st.markdown(''' :orange[MIXED]''')
                    st.write(explanation)
                elif tag[0] == 'inappropriate':
                    st.markdown(''' :red[INAPPROPRIATE]''')
                    st.write(explanation)
            st.divider()
            progress_bar.progress((i+1)/nb, progressbar((i+1)/nb))
        progress_bar.progress(100, "Ouf, terminé !")
if type == "un texte":
    topic = st.text_area("Entrez le sujet de l'article (important pour donner du contexte !)", "", height=50)
    question = st.text_area("Entrez la question à tester", "", height = 50)
    answer = st.text_area("Entrez la réponse correspondante", "", height=500)
    if question != '' and answer != '':
        with st.spinner('Wait for it'):
            response = title_4(title = topic, question=question, answer=answer)
            tag = re.findall(r'\[(.*)\]', response)
            explanation = re.sub(r'\[.*\]', '', response)
            if tag[0] == 'appropriate':
                st.markdown(''' :green[APPROPRIATE]''')
                st.write(explanation)
            elif tag[0] == 'mixed':
                st.markdown(''' :orange[MIXED]''')
                st.write(explanation)
            elif tag[0] == 'inappropriate':
                st.markdown(''' :red[INAPPROPRIATE]''')
                st.write(explanation)
