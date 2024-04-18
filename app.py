from flask import Flask, abort, request
from flask_cors import CORS
from tempfile import NamedTemporaryFile
import whisper
import torch
import yt_dlp
import os

# Check if NVIDIA GPU is available
torch.cuda.is_available()
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

model = whisper.load_model("base", device=DEVICE)

app = Flask(__name__)
CORS(app)

@app.route("/")
def run_streamlit():
    return "Run Streamlit app"


@app.route('/whisper', methods=['POST'])
def handler():
    if not request.files:
        abort(400)

    results = []

    for filename, handle in request.files.items():
        temp = NamedTemporaryFile()
        handle.save(temp)
        result = model.transcribe(temp.name)
        results.append({
            'filename': filename,
            'transcript': result['text'],
        })

    return {'results': results}

@app.route('/transcribe_youtube', methods=['POST'])
def transcribe_youtube():
    youtube_link = request.json['link']
    
    with NamedTemporaryFile(suffix=".mp4") as temp:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
            'outtmpl': temp.name,
            'postprocessors': [],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_link])
        
        result = model.transcribe(temp.name)
    
    return {'transcript': result['text']}