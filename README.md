# Estimulo Video Knowledge

## Descrição
Este projeto é uma aplicação web que transcreve vídeos do YouTube utilizando a API Whisper. O frontend é construído com Streamlit e o backend é desenvolvido em Flask. O banco de dados utilizado é o PostgreSQL, gerenciado com Docker.

## Estrutura do Projeto
- **Frontend**: Streamlit
- **Backend**: Flask
- **Banco de Dados**: PostgreSQL (Docker)
- **Gerenciamento de Contêineres**: Docker Compose

## Pré-requisitos
- Docker
- Docker Compose

Caso você deseje rodar o projeto na sua máquina local, você pode seguir as instruções de instalação [aqui](https://docs.docker.com/get-docker/).

## Como Executar

### 1. Clonar o Repositório
```bash
git clone https://github.com/VitorMoura01/estimulo.git
cd estimulo
```
### 2. Diretório

Certifique-se de que a estrutura do diretório do projeto esteja organizada da seguinte forma:

estimulo/
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py
│   └── db_repository.py
│
├── frontend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── streamlit_app.py
│   └── api_connect.py
│
└── docker-compose.yml

### 3. Iniciar os Contêineres
Na pasta raiz do projeto, execute o seguinte comando para iniciar os contêineres:

```bash
docker-compose up --build
```
Pronto! Agora o Frontend e o backend ja estão funcionando.

### 4. Testar a Aplicação
Frontend:
 - Streamlit App: http://localhost:8501

Backend: 
- Flask API: http://localhost:5000

Caso seja necessário, você pode verificar a porta e conectividade dos contêineres entrando neles.

Frontend:
```bash
docker exec -it streamlit_app bash
```
Backend:
```bash
docker exec -it flask_app bash
```

Dentro do contêiner Streamlit, você pode usar curl para verificar a conectividade:

```bash
apt-get update && apt-get install curl
curl http://flask_app:5000/get_txt
```

## Endpoints da API
### Transcrever Link do YouTube
URL: /transcribe_youtube
Método: POST
Parâmetros: {"link": "<URL_do_Video>"}

### Obter Base de Texto
URL: /get_txt
Método: GET

## Contribuições

- <a href="https://www.linkedin.com/in/vitor-moura-de-oliveira/">Vitor Moura</a>
- <a href="https://www.linkedin.com/in/lucas-vieira-376665208/">Lucas Vieira</a>
- <a href="https://www.linkedin.com/in/raduanmuarrek/">Raduan Muarrek</a>
