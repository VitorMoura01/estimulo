import requests

class API:
    def __init__(self, route):
        self.url = f'http://localhost:5000/{route}'

    def post(self, data=None, json=None):
        if json is not None:
            response = requests.post(self.url, json=json)
        else:
            response = requests.post(self.url, data=data)
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
        return self.get().content.decode('utf-8')