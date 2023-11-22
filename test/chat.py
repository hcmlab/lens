import os

import requests
import json
from time import perf_counter
from dotenv import load_dotenv


def post_stream(url, data):
    s = requests.Session()
    answer = ""
    with s.post(url, json=json.dumps(data), stream=True) as resp:
        for line in resp:
            if line:
                answer += line.decode()
                print(line.decode(), end=' ')
    return answer

# ENV
env = load_dotenv(r'../.env')
host = os.getenv('HOST')
port = os.getenv('PORT')


# Creating background context for llama
SYSTEM_PROMPT = "You are a helpful and funny virtual agent."
DATA_DESC = ""
DATA = ""

# Messages
url = f'http://{host}:{port}/assist'
payload = {
    "system_prompt": SYSTEM_PROMPT,
    "data": DATA,
    "data_desc": DATA_DESC
}

history = []
message = ''
while message != 'exit':
    message = input('User: ')
    if message == 'clear':
        history = []
        continue

    payload['message'] = message
    payload['history'] = history

    answer = post_stream(url, payload)

    history.append((message, answer))
    print('\n')
