import json

import requests
api_base="http://137.250.171.56:1337"
# Making a POST request with the stream parameter set to True to handle streaming responses
with requests.get(api_base + '/models') as response:
    print(response.content)

request = {
    'model': 'llama2',
    'provider': 'ollama',
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