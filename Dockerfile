FROM python:3.10-slim

WORKDIR /python-docker

COPY dockerrequirements.txt dockerrequirements.txt
RUN apt-get update && apt-get install git -y
# If are experiencing errors ImportError: cannot import name 'soft_unicode' from 'markupsafe'  please uncomment below
RUN pip3 install markupsafe==2.0.1
RUN pip3 install -r dockerrequirements.txt
RUN pip3 install yt-dlp
RUN pip3 install "git+https://github.com/openai/whisper.git" 
RUN apt-get install -y ffmpeg

COPY . .

EXPOSE 5000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
