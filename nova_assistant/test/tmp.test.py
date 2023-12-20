from litellm import completion

response = completion(
    model="ollama/llama2",
    messages=[{ "content": "respond in 20 words. who are you?","role": "user"}],
    api_base="http://137.250.171.154:5050",
    stream=True
)
print(response)
for chunk in response:
    print(chunk['choices'][0]['delta'])