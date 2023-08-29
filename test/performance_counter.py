import requests
import json
import pandas as pd
from hcai_datasets.hcai_nova_dynamic.hcai_nova_dynamic_iterable import HcaiNovaDynamicIterable
from llama2_wrapper.model import get_prompt
from pathlib import Path
from time import perf_counter
# tokenizer for length check
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained('..\\..\\..\\huggingface\\Llama-2-7b-chat-hf')


def get_promt_len(message, sp):
    prompt = get_prompt(message=message, chat_history=[], system_prompt=sp)
    input_ids = tokenizer([prompt], return_tensors="np")["input_ids"]
    return input_ids.shape[-1]

def post_stream(url, data):
    s = requests.Session()
    answer = ""
    with s.post(url, json=json.dumps(data), stream=True) as resp:
        for line in resp:
            if line:
                answer += line.decode()
                #print(line.decode(), end=' ')
    return answer

url = 'http://137.250.171.56:1337/assist'
payload = {
    "system_prompt": 'You are a helpful, respectful and honest assistant.',
    "data": 'Write a story about llamas',
    "data_desc": ""
}
t1_start = perf_counter()
input_token_length = get_promt_len(payload['data'], payload['system_prompt'])
print(input_token_length)
answer = post_stream(url, payload)
print(f"Elapsed time: {perf_counter()- t1_start}")
print(answer)


