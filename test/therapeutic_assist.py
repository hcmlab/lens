import requests
import json
import pandas as pd
from hcai_datasets.hcai_nova_dynamic.hcai_nova_dynamic_iterable import HcaiNovaDynamicIterable
from llama2_wrapper.model import get_prompt

# loading annotations from nova
roles = ["therapeut","patient"]
scheme = "transcript"
iterable = HcaiNovaDynamicIterable(
    db_config_path="nova_db.cfg",
    dataset="therapai",
    sessions=['99Z9_S03'],
    roles=roles,
    schemes=[scheme],
    annotator="whisperx_segment",
    frame_size="0ms",
)
session_data = iterable.to_single_session_iterator('99Z9_S03')

# tokenizer for length check
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained('..\\..\\..\\huggingface\\Llama-2-7b-chat-hf')

data_r0 = session_data.annos[f'{roles[0]}.{scheme}'].dataframe
data_r1 = session_data.annos[f'{roles[1]}.{scheme}'].dataframe

data_r0['role'] = roles[0]
data_r1['role'] = roles[1]

data_merged = pd.concat([data_r0, data_r1]).sort_values('from').drop(columns=['conf', 'from', 'to'])

# creating background context for llama
SYSTEM_PROMPT = "Your name is Nova. You are a therapeutic assistant, helping me analyse the interaction between a patient and the therapist. If you don't know the answer, please do not share false information. Do not create ficional examples. Under no circumstances should you add data to it. " \
    "I will now provide you with the data. Do not start any analysis unless I specifically ask for it."
DATA_DESC = "The data you are supposed to analyse is provided to you in list form, where each entry contains the transcript of a speaker at position 0 and the identity of the speaker at position 1."
DATA = f'This is the data: {data_merged.values.tolist()}'
f"This is the data: The {scheme} for the {roles[0]} is {session_data.annos[f'{roles[0]}.{scheme}'].dataframe.drop(columns=['conf']).to_string(sparsify=False, index=False)}. The {scheme} for the {roles[1]} is {session_data.annos[f'{roles[1]}.{scheme}'].dataframe.drop(columns=['conf']).to_string(sparsify=False, index=False)}"

def get_promt_len(history, message, system_prompt, data_desc, data):
   sp = "".join( [system_prompt, data_desc, data] )
   prompt = get_prompt(message=message, chat_history=history, system_prompt=sp)
   input_ids = tokenizer([prompt], return_tensors="np")["input_ids"]
   return input_ids.shape[-1]

def post_stream(url, data):
    s = requests.Session()
    answer = ""
    with s.post(url, json=json.dumps(data), stream=True) as resp:
        for line in resp:
            if line:
                answer += line.decode()
                print(line.decode(), end=' ')
    return answer

url = 'http://137.250.171.56:1337/assist'
payload = {
    "system_prompt": SYSTEM_PROMPT,
    "data_desc": DATA_DESC,
    "data": DATA
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

    input_token_length = get_promt_len(history=history, message=message, system_prompt=SYSTEM_PROMPT, data_desc=DATA_DESC, data=DATA)
    print(input_token_length)
    answer = post_stream(url, payload)
    history.append((message, answer))
    print('\n')
