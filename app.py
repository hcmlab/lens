import os
import json

import flask
from flask import Flask, request
from dotenv import load_dotenv
from distutils.util import strtobool
from waitress import serve
from llama2_wrapper import Llama2Wrapper
from typing import Iterator

# load environment
load_dotenv()
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


@app.route("/assist", methods=["POST"])
def assist():
    if request.method == "POST":
        user_request = request.get_json()
        if isinstance(user_request, str):
            user_request = json.loads(user_request)
        message = user_request.get("message", "")
        history = user_request.get("history", [])
        system_prompt = "".join(
            [
                user_request.get("system_prompt", DEFAULT_SYSTEM_PROMPT),
                user_request.get("data_desc", ""),
                user_request.get("data", ""),
            ]
        )

        temperature = user_request.get("temperature", DEFAULT_TEMPERATURE)
        max_new_tokens = user_request.get("max_new_tokens", DEFAULT_MAX_NEW_TOKENS)
        top_k = user_request.get("top_k", DEFAULT_TOP_K)
        top_p = user_request.get("top_p", DEFAULT_TOP_P)

        try:
            temperature = float(temperature)
        except:
            return flask.Response(f'ERROR: Temperature "{temperature}" is not a valid float.', 505)

        print(f'\nmessage="{message}",system_prompt={system_prompt},max_new_tokens={max_new_tokens},temp={temperature},top_k={top_k},top_p={top_p}\n')

        ret = generate(
            message=message,
            history=history,
            system_prompt=system_prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
        )
        return app.response_class(ret, mimetype="text/csv")


serve(app, host=HOST, port=PORT)
