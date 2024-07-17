FROM python:3.10-slim

WORKDIR /app

# Instala as dependências do sistema
RUN apt-get update && apt-get install -y git ffmpeg libpq-dev build-essential

# Copia e instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código para o container
COPY . .

# Exponha a porta 8501 para o Streamlit
EXPOSE 8501

# Comando para iniciar a aplicação Streamlit
CMD ["streamlit", "run", "streamlit_app.py"]
