import streamlit as st


def load(input, api):
    st.divider()
    st.subheader("Transcrição:")
    with st.spinner(text='Carregando...'):
        result = api.post_data(input)
    st.success('Concluído')
    st.text_area(label ="Resultado",value=result, height =100, disabled=True)