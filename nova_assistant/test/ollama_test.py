import json

from litellm import completion
import requests

BASE_URL = "http://137.250.171.154:5050"

def pull(model_name, insecure=False, callback=None):
    try:
        url = f"{BASE_URL}/api/pull"
        payload = {
            "name": model_name,
            "insecure": insecure
        }

        # Making a POST request with the stream parameter set to True to handle streaming responses
        with requests.post(url, json=payload, stream=True) as response:
            response.raise_for_status()

            # Iterating over the response line by line and displaying the details
            for line in response.iter_lines():
                if line:
                    # Parsing each line (JSON chunk) and extracting the details
                    chunk = json.loads(line)

                    # If a callback function is provided, call it with the chunk
                    if callback:
                        callback(chunk)
                    else:
                        # Print the status message directly to the console
                        print(chunk.get('status', ''), end='', flush=True)

                    # If there's layer data, you might also want to print that (adjust as necessary)
                    if 'digest' in chunk:
                        print(f" - Digest: {chunk['digest']}", end='', flush=True)
                        print(f" - Total: {chunk['total']}", end='', flush=True)
                        print(f" - Completed: {chunk['status']}", end='\n', flush=True)
                    else:
                        print('')
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

pull('llama2')

#resp = requests.post(})
#print(resp)
#breakpoint()

response = completion(
    model="ollama/llama2",
    messages=[{ "content": "respond in 20 words. who are you?","role": "user"}],
    api_base="http://137.250.171.154:5050"
)
print(response)