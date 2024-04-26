import json
from pathlib import Path
from typing import List, Optional, Union, Iterable, Dict, Any
from llama_index.core.schema import Document
from langchain.document_loaders.base import BaseLoader

import streamlit as st
from pages.Judge_Title import title_4
from pages.Summary_Assistant import summary_4
from pages.Spelling_Checker import coherence_spelling_4
import re


# Page title
st.sidebar.header("All in One")
st.title('All in One')

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()

st.write("A partir de l'URL, nous allons produire un résumé ainsi qu'un nouveau titre, vérifier la syntaxe, la cohérence de l'article et le respect de la charte, et enfin analyser séparément les titres-questions.")
st.markdown("**Attention, le traitement de la page est très long et prend au moins une bonne dizaine de minutes !**")

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
                text = titre + ' ' + answers
                docs.append(Document(text = text, metadata = {"category": metadata_category, "title": metadata_title, "subtitle": titre, "url": metadata_url}))               
        return docs
    
#load documents
file_path = "source/enriched_articles_05.json"
loader = JSONLoader(file_path = file_path)
data_sample = loader.load()

# Text input
url = st.text_area('Enter your url', '', height=50)

if url != '':
    chunks = [chunk for chunk in data_sample if chunk.metadata['url'] == url]
    old_title = [chunk for chunk in data_sample if chunk.metadata['url'] == url][0].metadata['title']
    st.container(border=True).write(old_title)
    with st.spinner('Wait for it...'):
        st.write(summary_4([chunk.text for chunk in chunks]))
    with st.spinner('Wait for it...'):
        st.write(coherence_spelling_4([chunk.text for chunk in chunks]))
    with st.spinner('Wait for it...'):
        for i,chunk in enumerate(chunks) :
            st.write(chunk.metadata['subtitle'])
            with st.spinner('Wait for it...'):
                answer = title_4(title = old_title, question = chunk.metadata['subtitle'], answer = chunk.text)
                tag = re.findall(r'\[(.*)\]', answer)
                explanation = re.sub(r'\[.*\]', '', answer)
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
