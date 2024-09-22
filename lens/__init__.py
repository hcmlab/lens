import os
import logging
import requests
import dotenv
dotenv.load_dotenv()

_MAJOR_VERSION = '0'
_MINOR_VERSION = '1'
_PATCH_VERSION = '0'

__version__ = '.'.join([
    _MAJOR_VERSION,
    _MINOR_VERSION,
    _PATCH_VERSION,
])

# def _openai_models(api_key = None):
#     try:
#         url = "https://api.openai.com/v1/models"
#         headers = {
#             "Authorization": f"Bearer {api_key}"
#         }
#         response = requests.get(url, headers=headers)
#        # models = [m['id'] for m in  response.json()['data']]
#         models = [x['id'] for x in  response.json()['data'] if x['owned_by'] == 'system' and x['id'].startswith('gpt')]
#         return models
#     except Exception as e:
#         logging.getLogger().error(e)
#         return []
#
# def _ollama_models(api_base):
#     try:
#         url = f"{api_base}/api/tags"
#         response = requests.get(url)
#         models = [m['name'] for m in response.json()['models'] if not 'text' in m['name']]
#         return models
#     except Exception as e:
#         logging.getLogger().error(e)
#         return []
#
# models_by_provider: dict = {
#     "ollama": _ollama_models(os.getenv('API_BASE_OLLAMA')),
#     "ollama_chat": _ollama_models(os.getenv('API_BASE_OLLAMA_CHAT')),
#     "openai": _openai_models(os.getenv('OPENAI_API_KEY'))
# }

if __name__ == '__main__':
    print(models_by_provider)