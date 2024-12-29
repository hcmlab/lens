# Description
LENS: Learning and Exploring through Natural language Systems is a lightweight webserver designed to use Large Language Models as tool for data exploration in human interactions.
LENS ist best used together with [NOVA](https://github.com/hcmlab/nova) and [DISCOVER](https://github.com/hcmlab/nova-server).

# Usage

LENS currently provides support for the [OpenAI](https://platform.openai.com/docs/overview) and the [OLLAMA](https://github.com/ollama/ollama/blob/main/docs/api.md).
So before you start make sure to either have access to an OpenAI API key or to set up a local OLLAMA server.

To install lens install python > 3.9 and run the following command in your terminal

`pip install hcai-lens` 

Create a file named `lens.env` at suitable location. 
Copy + Paste the contents from the [environment](#Environment) section to the newly created environment file and adapt the contents accordingly. 
Run LENS using the following command: 

`lens --env /path/to/lens.env`

# Environment

Example for .env file
```
# server
LENS_HOST = 127.0.0.1
LENS_PORT = 1337
LENS_CACHE_DUR = 600 #results pf /models are cached for the specified amount in seconds

# model
DEFAULT_MODEL = llama3.1

# API_BASES
API_BASE_OLLAMA = http://127.0.0.1:11434
API_BASE_OLLAMA_CHAT = http://127.0.0.1:11434

# api keys
OPENAI_API_KEY = <openai-api-key>
OLLAMA_API_KEY = None # Api keys are required for each model. Set to None if the provider doesn't need it.

# prompts
LENS_DEFAULT_MAX_NEW_TOKENS = 1024
LENS_DEFAULT_TEMPERATURE = 0.8
LENS_DEFAULT_TOP_K = 50
LENS_DEFAULT_TOP_P = 0.95
LENS_DEFAULT_SYSTEM_PROMPT = "Your name is LENS. You are a helpful assistant."
```


# API
LENS provides a REST API that can be called from any client. 
If applicable an endpoint accepts a request body as json JSON-formatted dictionary.
The API provides the following endpoints: 

<details>
 <summary><code>GET</code> <code><b>/models</b></code> <code>Retrieving a list of available models</code></summary>

##### Parameters

> None

##### Responses

> | http code | content-type              | example response                                                       |
> |-----------|---------------------------|------------------------------------------------------------------------|
> | `200`     | `application/json`        | `[{"id":"gpt-3.5-turbo-1106","max_tokens":16385,"provider":"openai"}]` |


</details>

---

<details>
 <summary><code>POST</code> <code><b>/assist</b></code> <code>application/json</code> <code>Sending a reqeust to a LLM and return the answer</code></summary>

##### Parameters

> | name           | type     | data type  | description                                                                     |
> |----------------|----------|------------|---------------------------------------------------------------------------------|
> | `model`        | required | str        | The id of the model as provided by `/models`                                    |
> | `provider`     | required | str        | The provider of the model as provided by `/models`                              |
> | `message`      | required | str        | The prompt that should be send to the model                                     |
> | `history`      | optional | list[list] | A history of previous question-answer-pairs in chronological order              |
> | `systemprompt` | optional | str        | Set of instructions that define the model behaviour                             |
> | `data_desc`    | optional | str        | An explanation of how context data should be interpreted by the model           |
> | `data`         | optional | str        | Additional context data for the llm                                             |
> | `stream`       | optional | bool       | If the answer should be streamed                                                |
> | `top_k`        | optional | int        | Select among the k most probable next tokens                                    |
> | `temperature`  | optional | int        | Degree of randomness to select next token among candidates                      |
> | `api_base`     | optional | str        | Overwrites the api_base of the server for the given provider/model combination  |  
> | `num_ctx`      | optional | str        | The numer of context tokens from the input that should be processed by the llm. |  


##### Responses

> | http code | content-type | response                                           |
> |-----------|--------------|----------------------------------------------------|
> | `200`     | `bytestring` | `A bytestring containing the UTF-8 encoded answer` |
                           
</details>


# Requests
```python
import requests
api_base="http://127.0.0.1:1337"
# Making a POST request with the stream parameter set to True to handle streaming responses
with requests.get(api_base + '/models') as response:
    print(response.content)

request = {
    'model': 'llama3.1',
    'provider': 'ollama_chat',
    'message': 'Add the cost of an apple to the last thing I asked you.',
    'system_prompt': 'Your name is LENS. You are a helpful shopping assistant.',
    'data_desc': 'The data is provided in the form of tuples where the first entry is the name of a fruit, and the second entry is the price of that fruit.',
    'data' : '("apple", "0.50"), ("avocado", "1.0"), ("banana", "0.80")',
    'stream': True,
    'top_k': 50,
    'top_p': 0.95,
    'temperature': 0.8,
    'history': [
        ["How much does a banana cost?", "Hello there! As a helpful shopping assistant, I'd be happy to help you find the price of a banana. According to the data provided, the cost of a banana is $0.80. So, one banana costs $0.80."]
    ],w
    'n_ctx' : 5000
}

with requests.post(api_base + '/assist', json=request) as response:
    print(response.content)
```

