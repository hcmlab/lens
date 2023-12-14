import json
import logging
import os
import litellm
import requests
import litellm.utils

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
        'created': None,
        'id': None,
        'owned_by': None,
        'object': 'model',
        'provider': None,
        'litellm_provider': None,
        'max_tokens': None,
        'api_base': None
        #model, custom_llm_provider, dynamic_api_key, api_base
    }
    try:
        # get keys set in .env
        environ_keys = os.environ.keys()
        valid_providers = []
        # for all valid providers, make a list of supported llms
        valid_models = []

        for provider in litellm.provider_list:
            # edge case litellm has together_ai as a provider, it should be togetherai
            provider = provider.replace("_", "")

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
            if provider == "customopenai":
                url = os.environ.get('API_BASE_'+provider.upper())
                resp = requests.get(url + '/models')
                if resp.status_code == 200:
                    try:
                        models_for_provider = json.loads(resp.content)['data']
                        # TODO litellm_provider is hardcoded to "openai". This indicates always a chat usecase whicht might not be the case. https://docs.litellm.ai/docs/providers/custom_openai_proxy
                        models_for_provider = [template.copy() | {'api_base' : url, 'provider' : provider, 'litellm_provider' : 'openai'} | m for m in models_for_provider]
                    except:
                        logging.log(f'Could not parse get_model response data {resp.content} from {url}')
            else:
                litellm.utils.get_llm_provider('gpt-3.5-turbo')
                model_list = litellm.models_by_provider.get(provider, [])
                models_for_provider = [template.copy() | {'id' : m, 'provider' : litellm.utils.get_llm_provider(m)[1] } | litellm.utils.get_model_info(m) for m in model_list]

            valid_models.extend(models_for_provider)
        return valid_models
    except:
        return [] # NON-Blocking

if __name__ == '__main__':
    import dotenv
    dotenv.load_dotenv()
    test = get_valid_models()
    breakpoint()