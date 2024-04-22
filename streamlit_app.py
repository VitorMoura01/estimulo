import streamlit as st
from api_connect import api_connect 
from loader import loader


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
        youtube_link = 'https://www.youtube.com/'
        link = st.text_input('Link do YouTube')

        if link.startswith(youtube_link):
            loader.load(link, ytb_api)
        else:
            st.warning('Insira um link válido do YouTube (https://www.youtube.com/)')

def config():

    st.set_page_config(
    page_title="Estimulo KnowledgeBase",
    page_icon=":🧠:",
    layout="centered",
    initial_sidebar_state="collapsed"
    )

if __name__ == '__main__':
    run_app()