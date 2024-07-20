FROM python:3.10-slim

WORKDIR /app

# Instala as dependências do sistema
RUN apt-get update && apt-get install -y git ffmpeg libpq-dev build-essential

# Copia e instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# Comando para iniciar a aplicação Flask
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
