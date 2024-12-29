# import sys
# import os
# #sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import flask
import os
import logging
from flask import Flask, request
from waitress import serve
from flask import stream_with_context
from flask_caching import Cache
from litellm import completion
import argparse
import dotenv
from lens import __version__
from lens import utils as lens_utils
from pathlib import Path
import requests


def _run():

    parser = argparse.ArgumentParser(
        description="Commandline arguments to configure the nova backend server"
    )
    parser.add_argument(
        "--env",
        type=str,
        default="",
        help="Path to the environment file to read config from",
    )


    # Parse cmdline arguments
    args = parser.parse_args()

    # Load environment variables
    env_path = Path(dotenv.find_dotenv())
    if args.env:
        env_path = Path(args.env)
        if not env_path.is_file():
            raise FileNotFoundError(f'.env file not found at {env_path} ')
    if env_path.is_file():
        print(f'Loading environment from {env_path.resolve()}')
        dotenv.load_dotenv(env_path, verbose=True, override=True)

    # Set global values
    default_system_prompt = os.getenv("LENS_DEFAULT_SYSTEM_PROMPT", "")
    default_max_new_tokens = int(os.getenv("LENS_DEFAULT_MAX_NEW_TOKENS", 1024))
    default_temperature = float(os.getenv("LENS_DEFAULT_TEMPERATURE", 0.8))
    default_top_k = int(os.getenv("LENS_DEFAULT_TOP_K", 50))
    default_top_p = float(os.getenv("LENS_DEFAULT_TOP_P", 0.95))
    default_model = os.getenv("LENS_DEFAULT_MODEL")
    host = os.getenv("LENS_HOST", "127.0.0.1")
    port = int(os.getenv("LENS_PORT", 1337))


    # Initially loading available models
    # models_by_provider: dict = {
    #     "ollama": _ollama_models(os.getenv('API_BASE_OLLAMA')),
    #     "ollama_chat": _ollama_models(os.getenv('API_BASE_OLLAMA_CHAT')),
    #     "openai": _openai_models(os.getenv('OPENAI_API_KEY'))
    # }

    # building the app
    print(f"Starting LENS v{__version__}...")
    config = {
        "DEBUG": True,          # some Flask specific configs
        "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
        "CACHE_DEFAULT_TIMEOUT": 300
    }
    # tell Flask to use the above defined config
    app = Flask(__name__)
    app.config.from_mapping(config)
    cache = Cache(app)


    _custom_provider = ['hcai', 'customopenai']

    @app.route("/models", methods=["POST", "GET"])
    @cache.cached(timeout=600) # Cache results for 10 Minutes
    def get_models():
        return lens_utils.get_valid_models()

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
                    user_request.get("system_prompt", default_system_prompt),
                    user_request.get("data_desc", ""),
                    user_request.get("data", ""),
                ]
            )

            temperature = user_request.get("temperature", default_temperature)
            max_new_tokens = user_request.get("max_new_tokens", default_max_new_tokens)
            top_k = user_request.get("top_k", default_top_k)
            top_p = user_request.get("top_p", default_top_p)
            model = user_request.get("model", default_model)
            num_ctx = user_request.get("num_ctx", None)
            stream = user_request.get("stream", True)
            provider = user_request.get("provider", None)
            api_base = user_request.get("api_base", None)
            resp_format = user_request.get("resp_format", None)
            # TODO PARSE CORRECTLY
            force_deterministic = user_request.get("enforce_determinism", 'False')

            if isinstance(force_deterministic, str):
                force_deterministic = False if force_deterministic == 'False' else True
            custom_llm_provider = None

            try:
                temperature = float(temperature)
            except:
                return flask.Response(f'ERROR: Temperature "{temperature}" is not a valid float.', 505)

            messages = [{'role': 'system', 'content': system_prompt}]

            for h in history:
                messages.append({'role': 'user', 'content': h[0]})
                messages.append({'role': 'assistant', 'content': h[1]})

            messages.append({'role': 'user', 'content': user_message})
            print(messages)

            # TODO DEPENDING ON THE PROVIDER WE LOAD A DIFFERENT BACKEND
            if not provider:
                flask.abort(400, 'Provider is none')

            if api_base is None and provider is not None:
                    prov_ = provider.split('_')[0]
                    api_base = os.getenv('API_BASE_' + prov_.upper())

            # Build response
            if provider in _custom_provider:
                custom_llm_provider = 'openai'
            if provider != 'openai':
                model = provider + '/' + model

            # Send initial message without content to
            if force_deterministic:
                temperature = 0
                response = completion(
                    model=model,
                    messages=[{'role': 'system', 'content': 'ignore this'}],
                    stream=False,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    max_tokens=1,
                    api_base=api_base,
                    custom_llm_provider=custom_llm_provider, # litellm will use the openai.Completion to make the request
                    additional_drop_params=["extra_body"]
                )
                print(response)
                print('Dummy request to enforce determination processed')

            if resp_format is None:
                response = completion(
                    model=model,
                    num_ctx=num_ctx,
                    messages=messages,
                    stream=stream,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    max_tokens=max_new_tokens,
                    api_base=api_base,
                    custom_llm_provider=custom_llm_provider, # litellm will use the openai.Completion to make the request
                    additional_drop_params=["extra_body"]

                )
            else:
                response = completion(
                    model=model,
                    num_ctx=num_ctx,
                    messages=messages,
                    stream=stream,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    max_tokens=max_new_tokens,
                    api_base=api_base,
                    custom_llm_provider=custom_llm_provider, # litellm will use the openai.Completion to make the request
                    format=resp_format,
                    additional_drop_params=["extra_body"]

                )

            if stream:
                print('Streaming answer')
                def generate(response):
                    for chunk in response:
                        yield chunk.choices[0].delta.content

                return app.response_class(stream_with_context(generate(response)))
            else:
                print('Returning answer')
                #return response#app.response_class(response)
                return response.choices[0].model_extra['message'].content


    logger = logging.getLogger('waitress')
    logger.setLevel(logging.DEBUG)
    serve(app, host=host, port=port)


if __name__ == '__main__':
    _run()