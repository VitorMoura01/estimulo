from tempfile import NamedTemporaryFile
import whisper
import torch
import yt_dlp
import db_repository as db


# Check if NVIDIA GPU is available
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base", device=DEVICE)

def transcribe_file(file_path):
    result = model.transcribe(file_path)
    return result['text']

def transcribe_youtube_link(youtube_link):
    conn = db.connect_to_db()
    db.create_table(conn)
    response_value = db.verify_existance(conn, youtube_link)
    results = []

    if response_value == 1:
        results.append({
            'filename': "ERRO",
            'transcript': 'Data already exists in the table',
        })
        return {'results': results}
    elif response_value == 0:
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

def post_link(link, transcript):
    conn = db.connect_to_db()
    db.create_table(conn)
    db.insert_into_table(conn, link, transcript)
    db.close_connection(conn)
