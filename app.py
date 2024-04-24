from flask import Flask, abort, request, send_file, make_response
from flask_cors import CORS
from tempfile import NamedTemporaryFile
import whisper
import torch
import yt_dlp
import db_repository as db
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

def post_link(link, transcript):
    conn = db.connect_to_db()
    db.create_table(conn)
    print('Table created successfully')
    db.insert_into_table(conn, link, transcript)
    print('Values inserted successfully')
    db.close_connection(conn)
    print('Connection closed successfully')

@app.route('/get_txt', methods=['GET'])
def get_txt():
    conn = db.connect_to_db()
    db.create_table(conn)
    print('Table created successfully')
    txt_path = db.select_all_and_create_txt(conn)
    db.close_connection(conn)
    print('Connection closed successfully')

    if os.path.isfile(txt_path):
        return send_file(txt_path, as_attachment=True)
    else:
        return make_response(f"File '{txt_path}' not found.", 404)

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
    results = []
    temp = NamedTemporaryFile()

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
        'outtmpl': temp.name,
        'postprocessors': [],
    }

    ydl = yt_dlp.YoutubeDL(ydl_opts)
    status_code = ydl.download([youtube_link])
    if status_code == 0:
        print("Video downloaded and saved to " + temp.name)
    else:
        print("Video download failed")

    result = model.transcribe(f"{temp.name}.mp4")
    results.append({
        'filename': temp.name,
        'transcript': result['text'],
    })
    post_link(youtube_link, result['text'])

    return {'results': results}