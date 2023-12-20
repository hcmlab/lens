import os
import json

import flask
from flask import Flask, request
from dotenv import load_dotenv
from distutils.util import strtobool
from waitress import serve
from nova_assistant.provider.hcai.llama2_wrapper import Llama2Wrapper
from typing import Iterator

# load environment
load_dotenv('../../local_llama.env')
DEFAULT_SYSTEM_PROMPT = os.getenv("DEFAULT_SYSTEM_PROMPT", "")
DEFAULT_MAX_NEW_TOKENS = int(os.getenv("DEFAULT_MAX_NEW_TOKENS", 1024))
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", 0.8))
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", 50))
DEFAULT_TOP_P = float(os.getenv("DEFAULT_TOP_P", 0.95))

MAX_MAX_NEW_TOKENS = int(os.getenv("MAX_MAX_NEW_TOKENS", 2048))
MAX_INPUT_TOKEN_LENGTH = int(os.getenv("MAX_INPUT_TOKEN_LENGTH", 4000))
MODEL_PATH = os.getenv("MODEL_PATH")
DEVICE = os.getenv("DEVICE", "cpu")
LOAD_IN_8BIT = bool(strtobool(os.getenv("LOAD_IN_8BIT", "True")))
HOST = os.getenv("LL_HOST", "127.0.0.1")
PORT = int(os.getenv("LL_PORT", 1338))
assert MODEL_PATH is not None, f"MODEL_PATH is required, got: {MODEL_PATH}"

config = {
    "model_name": MODEL_PATH,
    "load_in_8bit": LOAD_IN_8BIT,
    "device": DEVICE,
}

# load the model
llama2_wrapper = Llama2Wrapper(config)
llama2_wrapper.init_tokenizer()
llama2_wrapper.init_model()

# list of supported models
supported_models = [
    {
        "id": "llama7b",
        "object": "model",
        "created": 1702546785,
        "owned_by": "meta",
        "provider": "hcai",
    }

]

# defining helper
def ess_wrapper(g: Iterator, stream=True):

    if stream:
        for i, a in enumerate(g):
            yield 'data:' + \
                json.dumps(
                    {
                        "object": "chat.completion.chunk",
                        "choices": [{
                            "delta": {
                                "content": a,
                                "role": 'assistant',
                            },
                            "finish_reason": None,
                            "index": 0
                        },
                        ],
                        "created": "1"
                    }
                ) + '\n'
            yield '\n'
    else:
        _content = ''.join(g)
        return {
            "object":
                "chat.completion",
            "choices": [{
                "finish_reason": "stop",
                "index": 0,
                "message": {
                    "content":
                        "The sky, a canvas of blue,\nA work of art, pure and true,\nA",
                    "role": "assistant"
                }
            }],
            "id":
                "chatcmpl-7fbd6077-de10-4cb4-a8a4-3ef11a98b7c8",
            "created":
                1699290237.408061,
            "model":
                "togethercomputer/llama-2-70b-chat",
            "usage": {
                "completion_tokens": 18,
                "prompt_tokens": 14,
                "total_tokens": 32
            }
        }



def generate(
        message: str,
        history: list[tuple[str, str]],
        system_prompt: str,
        max_new_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
) -> Iterator[str]:
    if max_new_tokens > MAX_MAX_NEW_TOKENS:
        raise ValueError

    generator = llama2_wrapper.run(
        message, history, system_prompt, max_new_tokens, temperature, top_p, top_k
    )
    return generator


def check_input_token_length(
        message: str, chat_history: list[tuple[str, str]], system_prompt: str
) -> bool:
    input_token_length = llama2_wrapper.get_input_token_length(
        message, chat_history, system_prompt
    )
    if input_token_length > MAX_INPUT_TOKEN_LENGTH:
        return False
    else:
        return True


# building the app
print("Starting nova-assistant")
app = Flask(__name__)


# get supported models
@app.route('/models', methods=["GET"])
def get_models():
    #https://platform.openai.com/docs/api-reference/images/createVariation?lang=curl
    ret = json.dumps({"object": "list", "data": supported_models})
    for c in ['{', '}', '[', ']', ',']:
        ret = ret.replace(c, c + '\n ')
    return ret

# chat completion
@app.route('/v1//chat/completions', methods=["POST", "GET"])
@app.route('/chat/completions', methods=["POST"])
def chat_completion():
    print("got request for chat completion")
    data = request.json
    print("request data", data)

    history = []
    for m in data['messages']:
        if m['role'] == 'system':
            system_prompt = m['content']
        else:
            history.append((m['role'], m['content']))
    message = history[-1][1]
    history = history[:-1]

    temperature = data.get("temperature", DEFAULT_TEMPERATURE)
    max_new_tokens = data.get("max_tokens", DEFAULT_MAX_NEW_TOKENS)
    top_k = data.get("n", DEFAULT_TOP_K)
    top_p = data.get("top_p", DEFAULT_TOP_P)

    try:
        temperature = float(temperature)
    except:
        return flask.Response(f'ERROR: Temperature "{temperature}" is not a valid float.', 505)

    print(
        f'\nmessage="{message}",system_prompt={system_prompt},max_new_tokens={max_new_tokens},temp={temperature},top_k={top_k},top_p={top_p}\n')

    print("got request for chat completion")
    data = request.json
    print("request data", data)

    ret = generate(
        message=message,
        history=history,
        system_prompt=system_prompt,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
    )

    stream = data.get('stream', False)
    return app.response_class(ess_wrapper(ret, stream=stream), mimetype='text/event-stream')


serve(app, host=HOST, port=PORT)
