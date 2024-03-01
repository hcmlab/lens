# Description

# API
Nova Assistant has a REST API that can be called from any client. 
If applicable an endpoint accepts a reqeust body as json formatted dictionary.
The api provides the following endpoints: 

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

> | name           | type     | data type  | description                                                                    |
> |----------------|----------|------------|--------------------------------------------------------------------------------|
> | `model`        | required | str        | The id of the model as provided by `/models`                                   |
> | `provider`     | required | str        | The provider of the model as provided by `/models`                             |
> | `message`      | required | str        | The prompt that should be send to the model                                    |
> | `history`      | optional | list[list] | A history of previous question-answer-pairs in chronological order             |
> | `systemprompt` | optional | str        | Set of instructions that define the model behaviour                            |
> | `data_desc`    | optional | str        | An explanation of how context data should be interpreted by the model          |
> | `data`         | optional | str        | Additional context data for the llm                                            |
> | `stream`       | optional | bool       | If the answer should be streamed                                               |
> | `top_k`        | optional | int        | Select among the k most probable next tokens                                   |
> | `temperature`  | optional | int        | Degree of randomness to select next token among candidates                     |
> | `api_base`     | optional | str        | Overwrites the api_base of the server for the given provider/model combination |  


##### Responses

> | http code | content-type | response                                           |
> |-----------|--------------|----------------------------------------------------|
> | `200`     | `bytestring` | `A bytestring containing the UTF-8 encoded answer` |
                           
</details>


# Environment
Example for .env file
```
# server
HOST = 127.0.0.1
PORT = 1337

# model
DEFAULT_MODEL = gpt-3.5-turbo

# API_BASES
API_BASE_OLLAMA = http://127.0.0.1:11434

# api keys
OPENAI_API_KEY = <openai-api-key>
OLLAMA_API_KEY = None

# prompts
DEFAULT_MAX_NEW_TOKENS = 1024
DEFAULT_TEMPERATURE = 0.8
DEFAULT_TOP_K = 50
DEFAULT_TOP_P = 0.95
DEFAULT_SYSTEM_PROMPT = "Your name is Nova. You are a a helpful assistant."
```

# Requests
```python
import requests
api_base="http://127.0.0.1:1337"
# Making a POST request with the stream parameter set to True to handle streaming responses
with requests.get(api_base + '/models') as response:
    print(response.content)

request = {
    'model': 'llama2',
    'provider': 'ollama_chat',
    'message': 'Add the cost of an apple to the last thing I asked you.',
    'system_prompt': 'Your name is Nova. You are a a helpful shopping assistant.',
    'data_desc': 'The data is provided in the form of tuples where the first entry is the name of a fruit, and the second entry is the price of that fruit.',
    'data' : '("apple", "0.50"), ("avocado", "1.0"), ("banana", "0.80")',
    'stream': True,
    'top_k': 50,
    'top_p': 0.95,
    'temperature': 0.8,
    'history': [
        ["How much does a banana cost?", "Hello there! As a helpful shopping assistant, I'd be happy to help you find the price of a banana. According to the data provided, the cost of a banana is $0.80. So, one banana costs $0.80."]
    ]
}

with requests.post(api_base + '/assist', json=request) as response:
    print(response.content)
```

