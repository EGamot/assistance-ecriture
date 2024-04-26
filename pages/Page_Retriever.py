import json
from pathlib import Path
from typing import List, Optional, Union, Iterable, Dict, Any
from llama_index.core.schema import Document
from langchain.document_loaders.base import BaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.node_parser import LangchainNodeParser

import streamlit as st


# Page title
st.sidebar.header("Page Retriever")
st.title('Page Retriever')

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()

st.write("A partir d'un mot-clé, on retrouve tous les articles correspondant.")

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
file_path = r"source\enriched_articles_05.json"
loader = JSONLoader(file_path = file_path)
data_sample = loader.load()

parser = LangchainNodeParser(RecursiveCharacterTextSplitter())
nodes_text = parser.get_nodes_from_documents(data_sample)

# Text input
query = st.text_area('Enter your keyword', '', height=50)

if query != '':
    with st.spinner("Wait for it..."):
        BM25retriever = BM25Retriever.from_defaults(nodes=nodes_text, similarity_top_k=200)
        nodes_query = BM25retriever.retrieve(query)
        links={}
        for node in [node for node in nodes_query if node.score>0.0] :
            if node.metadata['url'] in list(links):
                links[node.metadata['url']].append(node.metadata['subtitle'])
            else :
                links[node.metadata['url']]=[]
                links[node.metadata['url']].append(node.metadata['subtitle'])
        for i, key in enumerate(list(links)):
            if len(list(links))!=0:
                st.write(key)
                for question in links[key]:
                    st.write(question)
                st.divider()
        if links == {}:
            st.write("Pas de résultat.")
