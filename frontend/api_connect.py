import requests

class API:
    def __init__(self, route):
        self.url = f'http://flask_app:5000/{route}'

    def post(self, files=None, json=None):
        if json is not None:
            response = requests.post(self.url, json=json)
        else:
            response = requests.post(self.url, files=files)
        return self.handle_response(response)

    def get(self):
        response = requests.get(self.url)
        return self.handle_response(response)

    def handle_response(self, response):
        if response.status_code == 200:
            return response
        else:
            print("Error: Received status code", response.status_code)
            print("Response content:", response.content)


class TranscribeYoutubeAPI(API):
    def __init__(self):
        super().__init__('transcribe_youtube')

    def post_data(self, link):
        return self.post(json={'link': link}).json()['results'][0]['transcript']


class WhisperAPI(API):
    def __init__(self):
        super().__init__('whisper')

    def post_data(self, file):
        return self.post(files={'file': file}).json()['results'][0]['transcript']


class GetTxtAPI(API):
    def __init__(self):
        super().__init__('get_txt')

    def get_data(self):
        response = self.get()
        if response is not None:
            return response.content.decode('utf-8')
        else:
            return None