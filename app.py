import os
import json
from flask import Flask, request
from dotenv import load_dotenv
from distutils.util import strtobool
from waitress import serve
from llama2_wrapper import Llama2Wrapper
from typing import Iterator

# load environment
load_dotenv()
DEFAULT_SYSTEM_PROMPT = os.getenv("DEFAULT_SYSTEM_PROMPT", "")
MAX_MAX_NEW_TOKENS = int(os.getenv("MAX_MAX_NEW_TOKENS", 2048))
DEFAULT_MAX_NEW_TOKENS = int(os.getenv("DEFAULT_MAX_NEW_TOKENS", 1024))
MAX_INPUT_TOKEN_LENGTH = int(os.getenv("MAX_INPUT_TOKEN_LENGTH", 4000))
MODEL_PATH = os.getenv("MODEL_PATH")
DEVICE = os.getenv("DEVICE", 'cpu')
LOAD_IN_8BIT = bool(strtobool(os.getenv("LOAD_IN_8BIT", "True")))
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 1337))
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

# defining helper
def generate(
        message: str,
        history: list[tuple[str, str]],
        system_prompt: str,
        max_new_tokens: int,
        temperature: float,
        top_p: float,
        top_k: int,
) -> Iterator[list[tuple[str, str]]]:
    if max_new_tokens > MAX_MAX_NEW_TOKENS:
        raise ValueError

    generator = llama2_wrapper.run(
        message, history, system_prompt, max_new_tokens, temperature, top_p, top_k
    )
    return generator
    #try:
    #    first_response = next(generator)
    #    yield history + [(message, first_response)]
    #except StopIteration:
        #yield history + [(message, "")]
   # for response in generator:
   #     yield history + [(message, response)]


#def process_example(message: str) -> tuple[str, list[tuple[str, str]]]:
#    generator = generate(message, [], DEFAULT_SYSTEM_PROMPT, 1024, 1, 0.95, 50)
#    return generator
    #for x in generator:
    #    pass
    #return "", x


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

@app.route("/assist", methods=["POST"])
def assist():
    if request.method == "POST":
        user_request = json.loads(request.get_json())
        if isInstance(user_request, str)
            user_request = json.loads(user_request)
        message = user_request.get('message', '')
        history =  user_request.get('history', [])
        system_prompt = "".join( [user_request.get('system_prompt', DEFAULT_SYSTEM_PROMPT), user_request.get('data_desc', ''), user_request.get('data','') ])

        ret = generate(message=message, history=history, system_prompt=system_prompt, max_new_tokens=1024, temperature=1, top_p=0.95, top_k=50)
        return app.response_class(ret, mimetype='text/csv')

serve(app, host=HOST, port=PORT)
