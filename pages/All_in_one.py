
import streamlit as st
from pages.Judge_Title import title_4
from pages.Summary_Assistant import summary_4
from pages.Spelling_Checker import coherence_spelling_4
from source.knowledge_load import data_sample
import re

from st_pages import add_page_title

# Either this or add_indentation() MUST be called on each page in your
# app to add indendation in the sidebar
add_page_title()

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()

st.write("A partir de l'URL, nous allons produire un résumé ainsi qu'un nouveau titre, vérifier la syntaxe, la cohérence de l'article et le respect de la charte, et enfin analyser séparément les titres-questions.")
st.markdown("**Attention, le traitement de la page est très long et prend au moins une bonne dizaine de minutes !**")

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