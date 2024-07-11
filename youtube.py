import httplib2
import random
import time
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError, ResumableUploadError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets, HttpAccessTokenRefreshError
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from flask import jsonify, url_for, redirect

CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
httplib2.RETRIES = 1
MAX_RETRIES = 10
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

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
        except ResumableUploadError as e:
            if "quotaExceeded" in str(e):
                print("Quota exceeded error: %s" % e)
                raise
            else:
                raise

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
    try:
        youtube = get_authenticated_service()
        initialize_upload(youtube, file_path, title, description)
    except HttpAccessTokenRefreshError as e:
        print(f"Failed to upload file to YouTube: {e}")
        raise
    except ResumableUploadError as e:
        print(f"Failed to upload file to YouTube due to quota exceeded: {e}")
        raise

def get_youtube_auth_url():
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_UPLOAD_SCOPE)
    auth_uri = flow.step1_get_authorize_url(redirect_uri=url_for('oauth2callback', _external=True))
    return jsonify({'auth_url': auth_uri})

def verify_youtube_code(code, redirect_url='/'):
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_UPLOAD_SCOPE)
    flow.redirect_uri = url_for('oauth2callback', _external=True)
    credentials = flow.step2_exchange(code)

    storage = Storage("%s-oauth2.json" % CLIENT_SECRETS_FILE)
    storage.put(credentials)

    return redirect(redirect_url)
