import json
import flask
from flask import Flask, request
from dotenv import load_dotenv
from waitress import serve
from litellm import completion
from flask import stream_with_context
import os

# load environment
load_dotenv()

DEFAULT_SYSTEM_PROMPT = os.getenv("DEFAULT_SYSTEM_PROMPT", "")
DEFAULT_MAX_NEW_TOKENS = int(os.getenv("DEFAULT_MAX_NEW_TOKENS", 1024))
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", 0.8))
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", 50))
DEFAULT_TOP_P = float(os.getenv("DEFAULT_TOP_P", 0.95))
MAX_MAX_NEW_TOKENS = int(os.getenv("MAX_MAX_NEW_TOKENS", 2048))
MAX_INPUT_TOKEN_LENGTH = int(os.getenv("MAX_INPUT_TOKEN_LENGTH", 4000))
MODEL = os.getenv("MODEL")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 1337))

# building the app
print("Starting nova-assistant")
app = Flask(__name__)


def stream_response(response):
    for chunk in response:
        yield chunk


@app.route("/assist", methods=["POST", "GET"])
def assist():
    if request.method == "POST":
        user_request = request.get_json()
        if isinstance(user_request, str):
            user_request = json.loads(user_request)
        user_message = user_request.get("message", "")
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
        model = user_request.get("model", MODEL)

        try:
            temperature = float(temperature)
        except:
            return flask.Response(f'ERROR: Temperature "{temperature}" is not a valid float.', 505)

        print(
            f'\nmessage="{user_message}",system_prompt={system_prompt},max_new_tokens={max_new_tokens},temp={temperature},top_k={top_k},top_p={top_p}\n')

        messages = [{'role': 'system', 'content': system_prompt}]

        for h in history:
            messages.append({'role': 'user', 'content': h[0]})
            messages.append({'role': 'assistant', 'content': h[1]})

        messages.append({'role': 'user', 'content': user_message})

        if 'ollama' in model:
            api_base = os.getenv('API_BASE_LOCAL_LLAMA')
        elif 'custom' in model:
            api_base = os.getenv('API_BASE_CUSTOM_LLAMA')
        else:
            api_base = None


        response = completion(
            model=model,
            messages=messages,
            stream=True,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_new_tokens,
            api_base=api_base,
            custom_llm_provider="openai" # litellm will use the openai.Completion to make the request
        )


        def generate(response):
            for chunk in response:
                yield chunk.choices[0].delta.content

        return app.response_class(stream_with_context(generate(response)))

import logging
logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)
serve(app, host=HOST, port=PORT)