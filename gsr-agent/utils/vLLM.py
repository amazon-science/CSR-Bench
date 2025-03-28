import json
import requests

class LocalLLM:
    def __init__(self, system_prompt, model_id='meta-llama/Meta-Llama-3-8B-Instruct', max_tokens=512):
        self.system_prompt = system_prompt
        self.model_id = model_id
        self.max_tokens = max_tokens
        self.url = 'http://localhost:8000/v1/completions'
        self.headers = {"Content-Type": "application/json"}

    def query(self, input_str):
        user_message = {"role": "user", "content": f"{input_str}"}
        messages = [user_message]

        body = json.dumps({
            "model": self.model_id,
            "prompt": self.system_prompt + input_str,
            "max_tokens": self.max_tokens,
            # "temperature": 0.9
        })

        response = requests.post(self.url, headers=self.headers, data=body)

        if response.status_code == 200:
            response_body = response.json()
            return response_body['choices'][0]['text']
        else:
            return f"Error: {response.status_code}, {response.text}"

# Example usage of LocalLLM class
system_prompt = "Please introduce San Francisco."
system_prompt = "Please anwering in Chinese."
system_prompt = "Answer using Emoji."
# system_prompt = "Please answer precisely and concisely."
local_llm = LocalLLM(system_prompt=system_prompt)

example_questoin = "Where is Seattle?"
response = local_llm.query(example_questoin)
print(response)

while True:
    input_str = input("Enter a query: ")
    if input_str == "exit":
        break

    response = local_llm.query(input_str)
    print(response)
