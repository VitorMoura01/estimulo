from flask import Flask, request, abort, jsonify, redirect, url_for, send_file, make_response
from flask_cors import CORS
from tempfile import NamedTemporaryFile
import whisper
import torch
import yt_dlp
import db_repository as db
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
import httplib2
import random
import time

CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
httplib2.RETRIES = 1
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# Check if NVIDIA GPU is available
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base", device=DEVICE)

app = Flask(__name__)
CORS(app)

def get_authenticated_service():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_UPLOAD_SCOPE)
    storage = Storage("%s-oauth2.json" % CLIENT_SECRETS_FILE)
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        flags = argparser.parse_args(args=[])
        flags.noauth_local_webserver = True
        credentials = run_flow(flow, storage, flags)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))

def resumable_upload(insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print("Video id '%s' was successfully uploaded." % response['id'])
                else:
                    raise Exception("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                raise Exception("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)

def initialize_upload(youtube, file_path, title, description, category="22", keywords="", privacy_status="public"):
    tags = keywords.split(",") if keywords else None

    body = dict(
        snippet=dict(
            title=title,
            description=description,
            tags=tags,
            categoryId=category
        ),
        status=dict(
            privacyStatus=privacy_status
        )
    )

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)

def upload_to_youtube(file_path, title, description):
    youtube = get_authenticated_service()
    initialize_upload(youtube, file_path, title, description)

@app.route("/")
def run_streamlit():
    return "Run Streamlit app"

@app.route('/get_txt', methods=['GET'])
def get_txt():
    conn = db.connect_to_db()
    db.create_table(conn)
    txt_path = db.select_all_and_create_txt(conn)
    db.close_connection(conn)
    print(f"File '{txt_path}' created successfully")

    if os.path.isfile(txt_path):
        return send_file(txt_path, as_attachment=True)
    else:
        return make_response(f"File '{txt_path}' not found.", 404)

@app.route('/whisper', methods=['POST'])
def handler():
    if not request.files:
        abort(400)

    results = []
    file_storage = request.files['file']
    filename = file_storage.filename
    for filename, handle in request.files.items():
        temp = NamedTemporaryFile(delete=False)
        handle.save(temp.name)
        result = model.transcribe(temp.name)
        results.append({
            'filename': filename,
            'transcript': result['text'],
        })
        file_storage = request.files['file']
        filename = file_storage.filename.replace('.mp4', '')
        print('Filename:', filename)
        print('Uploading to YouTube...')
        upload_to_youtube(temp.name, filename, result['text'])
        print('Upload complete')
        os.remove(temp.name)

    return {'results': results}

@app.route('/transcribe_youtube', methods=['POST'])
def transcribe_youtube():
    youtube_link = request.json['link']

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

@app.route('/youtube_auth_url', methods=['GET'])
def youtube_auth_url():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_UPLOAD_SCOPE)
    auth_uri = flow.step1_get_authorize_url(redirect_uri=url_for('oauth2callback', _external=True))
    return jsonify({'auth_url': auth_uri})

@app.route('/oauth2callback', methods=['GET'])
def oauth2callback():
    code = request.args.get('code')
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_UPLOAD_SCOPE)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    credentials = flow.step2_exchange(code)

    storage = Storage("%s-oauth2.json" % CLIENT_SECRETS_FILE)
    storage.put(credentials)

    return redirect('/')

@app.route('/youtube_verify_code', methods=['POST'])
def youtube_verify_code():
    code = request.json['code']
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_UPLOAD_SCOPE)
    credentials = flow.step2_exchange(code)

    storage = Storage("%s-oauth2.json" % CLIENT_SECRETS_FILE)
    storage.put(credentials)

    return jsonify({'message': 'Authentication successful'})
