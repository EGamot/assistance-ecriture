from langchain.text_splitter import RecursiveCharacterTextSplitter
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.node_parser import LangchainNodeParser
from llama_index.core.schema import TextNode

import streamlit as st
from st_pages import add_page_title
from source.knowledge_load import data_sample

# Either this or add_indentation() MUST be called on each page in your
# app to add indendation in the sidebar
add_page_title()

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()

st.write("A partir d'un mot-clé, on retrouve tous les articles correspondant.")

parser = LangchainNodeParser(RecursiveCharacterTextSplitter())
nodes_text = parser.get_nodes_from_documents(data_sample)
nodes = [TextNode(
            text=nodes_text[i].metadata["subtitle"] + " : " + nodes_text[i].text,
            id_=nodes_text[i].id_,
            metadata={
                'category': nodes_text[i].metadata['category'],
                'subtitle': nodes_text[i].metadata['subtitle'],
                'title': nodes_text[i].metadata['title'],
                'url': nodes_text[i].metadata["url"]
            }
        )
            for i in range(len(nodes_text))
        ]
# Text input
query = st.text_area('Enter your keyword', '', height=50)

if query != '':
    with st.spinner("Wait for it..."):
        BM25retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=200)
        nodes_query = BM25retriever.retrieve(query)
        st.text_area(nodes_query)
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
