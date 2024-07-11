from flask import Flask, request, abort, jsonify, redirect, url_for, send_file, make_response
from flask_cors import CORS
from tempfile import NamedTemporaryFile
import os
import db_repository as db
from whisper_service import transcribe_file, transcribe_youtube_link
from youtube import CLIENT_SECRETS_FILE, upload_to_youtube, get_youtube_auth_url, verify_youtube_code
from oauth2client.file import Storage

app = Flask(__name__)
CORS(app)

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
        transcript = transcribe_file(temp.name)
        results.append({
            'filename': filename,
            'transcript': transcript,
        })
        file_storage = request.files['file']
        filename = file_storage.filename.replace('.mp4', '')
        print('Uploading to YouTube...')
        # upload_to_youtube(temp.name, filename, transcript)
        print('Upload complete')
        os.remove(temp.name)

    return jsonify({'results': results}), 200

@app.route('/transcribe_youtube', methods=['POST'])
def transcribe_youtube():
    youtube_link = request.json['link']
    return transcribe_youtube_link(youtube_link)

@app.route('/youtube_auth_url', methods=['GET'])
def youtube_auth_url():
    return get_youtube_auth_url()

@app.route('/oauth2callback', methods=['GET'])
def oauth2callback():
    code = request.args.get('code')
    return verify_youtube_code(code, redirect_url='/')

@app.route('/youtube_verify_code', methods=['POST'])
def youtube_verify_code():
    code = request.json['code']
    return verify_youtube_code(code)

@app.route('/clear_credentials', methods=['GET'])
def clear_credentials():
    storage = Storage("%s-oauth2.json" % CLIENT_SECRETS_FILE)
    storage.delete()
    return jsonify({'message': 'Credentials cleared'}), 200

if __name__ == '__main__':
    app.run(debug=True)
