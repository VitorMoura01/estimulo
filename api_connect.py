import requests

class api_connect:
    def __init__(self, route):
        self.url = f'http://localhost:5000/{route}'

    def post_data(self, body):
        if self.url == 'http://localhost:5000/transcribe_youtube':
            response = requests.post(self.url, json={'link': body})
        elif self.url == 'http://localhost:5000/whisper':
            response = requests.post(self.url, files={'file': body})
        transcript = response.json()['results'][0]['transcript']
        
        if response.status_code == 200:
            try:
                return transcript
            except ValueError:
                print("Error: Response is not valid File.")
                print("Response content:", response.content)
        else:
            print("Error: Received status code", response.status_code)
            print("Response content:", response.content)