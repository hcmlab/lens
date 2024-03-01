import os
import logging
import requests
import dotenv
dotenv.load_dotenv()

def _openai_models(api_key = None):
    try:
        url = "https://api.openai.com/v1/models"
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        response = requests.get(url, headers=headers)
       # models = [m['id'] for m in  response.json()['data']]
        models = [x['id'] for x in  response.json()['data'] if x['owned_by'] == 'system' and x['id'].startswith('gpt')]
        return models
    except Exception as e:
        logging.getLogger().error(e)
        return []

def _ollama_models(api_base):
    try:
        url = f"{api_base}/api/tags"
        response = requests.get(url)
        models = [m['name'] for m in response.json()['models'] if not 'text' in m['name']]
        return models
    except Exception as e:
        logging.getLogger().error(e)
        return []

# TODO Is only loaded once on startup. Change to loading on demnand
# Explicitly overwriting l
models_by_provider: dict = {
    "ollama": _ollama_models(os.getenv('API_BASE_OLLAMA')),
    "ollama_chat": _ollama_models(os.getenv('API_BASE_OLLAMA')),
    "openai": _openai_models(os.getenv('OPENAI_API_KEY'))
}

if __name__ == '__main__':
    # import dotenv
    # dotenv.load_dotenv()
    # oai_models = _openai_models(os.getenv('OPENAI_API_KEY'))
    # ollama_models = _ollama_models(os.getenv('API_BASE_OLLAMA'))
    # breakpoint()
    print(models_by_provider)