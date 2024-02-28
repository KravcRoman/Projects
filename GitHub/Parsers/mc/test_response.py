import requests


URL = 'http://127.0.0.1:4216/start_parsing'

response = requests.post(URL)

print(response.text)
