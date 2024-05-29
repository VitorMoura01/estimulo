from io import BytesIO
import unicodedata
import zipfile
from tempfile import TemporaryDirectory
import os
import re
import pandas as pd
import requests
import streamlit as st
from api_connect import TranscribeYoutubeAPI, WhisperAPI, GetTxtAPI 

def config():
    st.set_page_config(
    page_title="Estimulo KnowledgeBase",
    page_icon=":🧠:",
    layout="centered",
    initial_sidebar_state="expanded"
    )

def handle_zip_file(uploaded_file):
    temp_dir = TemporaryDirectory()
    try:
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir.name)
        return temp_dir
    except zipfile.BadZipFile:
        st.error(f"Error: The file {uploaded_file.name} is not a valid zip file.")
        return None

def load(filename, func, *args, **kwargs):
    st.divider()
    st.subheader(f"Transcrição para {filename}:")
    with st.spinner(text='Carregando, pode demorar alguns minutos...'):
        response = func(*args, **kwargs)
        if isinstance(response, requests.Response):
            result_json = response.json()
            transcription = result_json['results'][0]['transcript']
        else:
            transcription = response
    st.success('Concluído')
    st.text_area(label ="Resultado",value=transcription, height =100, disabled=True, key=filename)
    
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
            load("vídeo do YouTube", ytb_api.post_data, link)
        else:
            st.info('Insira um link válido do YouTube (https://www.youtube.com/...)')

    with tab2:
        file_api = WhisperAPI()
        uploaded_file = st.file_uploader('File uploader', accept_multiple_files=False)

        if uploaded_file is not None:
            _, extension = os.path.splitext(uploaded_file.name)
            if extension.lower() == '.zip':
                temp_dir = handle_zip_file(uploaded_file)
                if temp_dir:
                    for root, _, files in os.walk(temp_dir.name):
                        for filename in files:
                            file_path = os.path.join(root, filename)
                            with open(file_path, 'rb') as file:
                                binary_file = BytesIO(file.read())
                                binary_file.name = filename
                                filename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode('ASCII')
                                load(filename, file_api.post, {'file': (filename, binary_file)})
                    temp_dir.cleanup()

            else:
                load(uploaded_file.name, file_api.post_data, uploaded_file)

        st.divider()


    
    txt_api = GetTxtAPI()
    data = txt_api.get_data()
    if data is not None:
        st.sidebar.title('Base de conhecimento')
        matches = re.findall(r'(\d+)\s+(https?://\S+)\s+(.+?)(?=\s+\d+|$)', data)
        df = pd.DataFrame(matches, columns=['id', 'link', 'transcript'])
        df = df.drop('id', axis=1)
        st.sidebar.download_button(
            label="Fazer o download",
            data=data,
            file_name='knowledgePrompt.txt',
            mime='text/plain',
            type='primary',
            use_container_width=True,
        )
        st.sidebar.write(df)
    else:
        st.warning('Não foi possível obter os dados.')

if __name__ == '__main__':
    run_app()