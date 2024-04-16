## What is Whisper?

Whisper is an automatic State-of-the-Art speech recognition system from OpenAI that has been trained on 680,000 hours 
of multilingual and multitask supervised data collected from the web. This large and diverse 
dataset leads to improved robustness to accents, background noise and technical language. In 
addition, it enables transcription in multiple languages, as well as translation from those 
languages into English. OpenAI released the models and code to serve as a foundation for building useful
applications that leverage speech recognition. 

## How to start with Docker
1. First of all if you are planning to run the container on your local machine you need to have Docker installed.
You can find the installation instructions [here](https://docs.docker.com/get-docker/).
2. Creating a folder for our files, lets call it `whisper-api`
3. Create a file called requirements.txt and add flask to it.
4. Create a file called Dockerfile 

In the Dockerfile we will add the following lines:

```dockerfile
FROM python:3.10-slim

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install git -y
RUN pip3 install -r requirements.txt
RUN pip3 install "git+https://github.com/openai/whisper.git" 
RUN apt-get install -y ffmpeg

COPY . .

EXPOSE 5000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
```  
### So what is happening exactly in the Dockerfile?
1. Choosing a python 3.10 slim image as our base image.
2. Creating a working directory called `python-docker`
3. Copying our requirements.txt file to the working directory
4. Updating the apt package manager and installing git
5. Installing the requirements from the requirements.txt file
6. installing the whisper package from github.
7. Installing ffmpeg
8. And exposing port 5000 and running the flask server.

## How to create our rout
1. Create a file called app.py where we import all the necessary packages and initialize the flask app and whisper.

## How to run the container?
1. Open a terminal and navigate to the folder where you created the files.
2. Run the following command to build the container:

```bash
docker build -t whisper-api .
```
3. Run the following command to run the container:

```bash
docker run -p 5000:5000 whisper-api
```

If you are having errors on MacOS please add `RUN pip3 install markupsafe==2.0.1` to the dockerfile. 

## How to test the API?
1. You can test the API by sending a POST request to the route `http://localhost:5000/whisper` with a file in it. Body should be form-data.
2. You can use the following curl command to test the API:

```bash
curl -F "file=@/path/to/file" http://localhost:5000/whisper
```

3. In result you should get a JSON object with the transcript in it.
