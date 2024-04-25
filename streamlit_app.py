import re
import streamlit as st
from api_connect import TranscribeYoutubeAPI, WhisperAPI, GetTxtAPI 

def config():
    st.set_page_config(
    page_title="Estimulo KnowledgeBase",
    page_icon=":🧠:",
    layout="centered",
    initial_sidebar_state="collapsed"
    )

def load(func, *args, **kwargs):
    st.divider()
    st.subheader("Transcrição:")
    with st.spinner(text='Carregando, pode demorar alguns minutos...'):
        result = func(*args, **kwargs)
    st.success('Concluído')
    st.text_area(label ="Resultado",value=result, height =100, disabled=True)
    
def run_app():
    config()
    
    st.title('Estimulo KnowledgeBase')
    st.subheader('Carregar vídeo via:')
    tab1, tab2 = st.tabs(['Vídeo do YouTube', 'Upload de arquivo'])

    with tab1:
        ytb_api = TranscribeYoutubeAPI()

        link = st.text_input('Link do YouTube')
        youtube_link_pattern = r'https://(www\.youtube\.com/|youtu\.be/)'

        if re.match(youtube_link_pattern, link):
            load(ytb_api.post_data, link)
        else:
            st.warning('Insira um link válido do YouTube (https://www.youtube.com/...)')

    with tab2:
        file_api = WhisperAPI()
        video_file = st.file_uploader('File uploader', accept_multiple_files=False)

        if video_file is not None:
            load(file_api.post_data, video_file)
    st.divider()


    
    txt_api = GetTxtAPI()
    data = txt_api.get_data()
    if data is not None:
        st.download_button(
            label="Download txt file",
            data=data,
            file_name='knowledgePrompt.txt',
            mime='text/plain',
        )
    else:
        st.warning('Não foi possível obter os dados.')

if __name__ == '__main__':
    run_app()