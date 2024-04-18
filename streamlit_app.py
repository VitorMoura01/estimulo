import streamlit as st
import time
import requests

def run_app():
    st.title('Transcrição de vídeo')
    tab1, tab2 = st.tabs(['Upload de arquivo', 'Vídeo do YouTube'])
    with tab1:
        video_file = st.file_uploader('File uploader', key=1, accept_multiple_files=False)
        if video_file is not None:
            with st.spinner(text='Transcrevendo...'):
                result = post_file(video_file)
                st.write(result)
            st.success('Transcrição concluída')
    with tab2:
        st.text_input('Link do YouTube')
        st.button('Transcrever')

def post_file(file):
    try:
        response = requests.post('http://localhost:5000/whisper', files={'file': file})
        transcript = response.json()['results'][0]['transcript']
        return transcript
    except:
        return "Erro ao enviar arquivo"

if __name__ == '__main__':
    run_app()