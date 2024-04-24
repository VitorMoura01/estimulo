import re
import streamlit as st
from api_connect import api_connect 
import loader as loader


def run_app():
    config()
    
    st.title('Estimulo KnowledgeBase')
    st.subheader('Carregar vídeo via:')
    tab1, tab2 = st.tabs(['Upload de arquivo', 'Vídeo do YouTube'])

    with tab1:
        file_api = api_connect('whisper')
        video_file = st.file_uploader('File uploader', accept_multiple_files=False)

        if video_file is not None:
            loader.load(video_file, file_api)

    with tab2:
        ytb_api = api_connect('transcribe_youtube')
        link = st.text_input('Link do YouTube')
        youtube_link_pattern = r'https://(www\.youtube\.com/|youtu\.be/)'

        if re.match(youtube_link_pattern, link):
            loader.load(link, ytb_api)
        else:
            st.warning('Insira um link válido do YouTube (https://www.youtube.com/...)')
    
    st.divider()
    
    st.download_button(
        label="Download txt file",
        data= api_connect('get_txt').get_data(),
        file_name='knowledgePrompt.txt',
        mime='text/plain',
    )

def config():

    st.set_page_config(
    page_title="Estimulo KnowledgeBase",
    page_icon=":🧠:",
    layout="centered",
    initial_sidebar_state="collapsed"
    )

if __name__ == '__main__':
    run_app()