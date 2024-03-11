import json
import logging
import os
import litellm
import requests
from nova_assistant import models_by_provider
import litellm.utils


def _get_max_position_embeddings(model_name):
    # Construct the URL for the config.json file
    config_url = f"https://huggingface.co/{model_name}/raw/main/config.json"

    try:
        # Make the HTTP request to get the raw JSON file
        response = requests.get(config_url)
        response.raise_for_status()  # Raise an exception for bad responses (4xx or 5xx)

        # Parse the JSON response
        config_json = response.json()

        # Extract and return the max_position_embeddings
        max_position_embeddings = config_json.get("max_position_embeddings")

        if max_position_embeddings is not None:
            return max_position_embeddings
        else:
            return None
    except requests.exceptions.RequestException as e:
        return None

def get_valid_models():
    """
    Returns a list of valid LLMs based on the set environment variables
    The list contains dictionaries extending the openai model format #https://platform.openai.com/docs/api-reference/images/createVariation?lang=curl

    Args:
        None

    Returns:
        list[dict]: A list of valid LLMs with detailed information
    Example:

        {
        'created': '1702546785',
        'id': 'llama7b',
        'owned_by': 'meta',
        'object': 'model',
        'provider': 'hcai',
        'litellm_provider': 'customopenai',
        'api_base': '127.0.0.1',
        }
    """

    template = {
        'id': None,
        'provider': None,
        'max_tokens': None,
        #'owned_by': None,
        #'created': None,
        #'object': 'model',
        #'litellm_provider': None,
        #'api_base': None
        #model, custom_llm_provider, dynamic_api_key, api_base
    }
    try:

        model_cost_map = litellm.model_cost

        # get keys set in .env
        environ_keys = os.environ.keys()
        valid_providers = []
        # for all valid providers, make a list of supported llms
        valid_models = []
        provider_list = litellm.provider_list + ['hcai']
        for provider in provider_list:
            # edge case litellm has together_ai as a provider, it should be togetherai
            #provider = provider.replace("_", "")

            # litellm standardizes expected provider keys to
            # PROVIDER_API_KEY. Example: OPENAI_API_KEY, COHERE_API_KEY
            expected_provider_key = f"{provider.upper()}_API_KEY"
            if expected_provider_key in environ_keys:
                # key is set
                valid_providers.append(provider)

        for provider in valid_providers:
            models_for_provider = []
            if provider == "azure":
                t = template.copy()
                t['id'] = "Azure-LLM"
                models_for_provider.append(t)
            # Custom Models
            if provider == "customopenai" or provider == "hcai":
                try:
                    url = os.environ.get('API_BASE_'+provider.upper(), '')
                    resp = requests.get(url + '/models')
                    if resp.status_code == 200:
                        models_for_provider = json.loads(resp.content)['data']
                        # TODO litellm_provider is hardcoded to "openai". This indicates always a chat usecase whicht might not be the case. https://docs.litellm.ai/docs/providers/custom_openai_proxy
                        models_for_provider = [template.copy() | {'api_base' : url, 'provider' : provider, 'litellm_provider' : 'openai'} | m for m in models_for_provider]
                except Exception as e:
                    logging.error(msg=f'Error retrieving data from {url} : {e}')
                    continue

            # LITELLM Models
            else:
                model_list = models_by_provider.get(provider, None)

                if model_list is None:
                    model_list = litellm.models_by_provider.get(provider, [])

                for model in model_list:
                    t = template.copy()
                    model_info = model_cost_map.get(model, {'input_cost_per_token': None, 'litellm_provider': None, 'max_tokens': None, 'mode':  None, 'output_cost_per_token': None})
                    t.update( {
                        'id': model,
                        'provider': provider,
                        #'litellm_provider': model_info['litellm_provider'],
                        'max_tokens': model_info['max_tokens']
                    })
                    models_for_provider.append(t)
                #model_list = litellm.models_by_provider.get(provider, [])
                #models_for_provider = [template.copy() | {'id' : m, 'provider' : provider, 'max_tokens' : _get_max_position_embeddings(m)} for m in model_list]

            valid_models.extend(models_for_provider)
        return valid_models
    except Exception as e:
        return [] # NON-Blocking

if __name__ == '__main__':
    import dotenv
    dotenv.load_dotenv()
    test = get_valid_models()
    breakpoint()