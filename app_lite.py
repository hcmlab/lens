import json
import flask
import os
import logging
from flask import Flask, request
from dotenv import load_dotenv
from waitress import serve
import utils
from flask import stream_with_context
from litellm import completion
from utils import get_valid_models

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


@app.route("/models", methods=["POST", "GET"])
def get_models():
    return get_valid_models()

@app.route("/assist", methods=["POST"])
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
        stream = user_request.get("stream", True)
        provider = user_request.get("provider", None)

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

        # TODO DEPENDING ON THE PROVIDER WE LOAD A DIFFERENT BACKEND
        if not provider:
            flask.abort(400, 'Provider is none')

        api_base = os.getenv('API_BASE_' + provider.upper())

        response = completion(
            model=model,
            messages=messages,
            stream=stream,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_new_tokens,
            api_base=api_base,
            custom_llm_provider="openai" # litellm will use the openai.Completion to make the request
        )

        if stream:
            def generate(response):
                for chunk in response:
                    yield chunk.choices[0].delta.content

            return app.response_class(stream_with_context(generate(response)))
        else:
            return app.response_class(response)

logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)
serve(app, host=HOST, port=PORT)
