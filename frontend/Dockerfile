FROM python:3.10-slim

RUN apt-get update && apt-get install -y netcat-openbsd

COPY wait.sh /wait.sh

WORKDIR /app

# Instala as dependências do sistema
RUN apt-get update && apt-get install -y git ffmpeg libpq-dev build-essential

# Copia e instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /wait.sh

CMD ["/wait.sh", "flask_app", "5000", "streamlit", "run", "streamlit_app.py"]
