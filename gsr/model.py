import boto3
import json
import re
import time
from botocore.config import Config
from .const import ERR_MSG
from .web_search import perplexity_search
from gsr.retriever import RetrievalEngine
import openai
import google.generativeai as genai

# class CoreAgent:
#     def __init__(self, system_prompt, model_id='anthropic.claude-3-haiku-20240307-v1:0', region_name='us-west-2', max_attempts=10, adaptive_mode='adaptive', max_tokens=4096):
#         self.system_prompt = system_prompt
#         self.model_id = model_id
#         self.max_tokens = max_tokens

#         self.config = Config(
#             retries={
#                 'max_attempts': max_attempts,
#                 'mode': adaptive_mode
#             }
#         )
#         self.brt = boto3.client(service_name='bedrock-runtime', region_name=region_name, config=self.config)

#     def query(self, input_str):
#         input_prompt = input_str

#         user_message = {"role": "user", "content": f"{input_prompt}"}
#         messages = [user_message]

#         body = json.dumps(
#             {
#                 "anthropic_version": "bedrock-2023-05-31",
#                 "max_tokens": self.max_tokens,
#                 "system": self.system_prompt,
#                 "messages": messages
#             }
#         )

#         FAILURE_COUNTER = 0
#         while True:
#             try:
#                 response = self.brt.invoke_model(body=body, modelId=self.model_id)
#                 break
#             except Exception as e:
#                 FAILURE_COUNTER += 1
#                 if FAILURE_COUNTER >= 5:
#                     break
#                 print(f'Exception encountered: {e}. Retrying in 60 seconds...')
                
#                 time.sleep(60)
#                 continue

#         if FAILURE_COUNTER >= 5:
#             return ERR_MSG

#         response_body = json.loads(response.get('body').read())

#         return response_body['content'][0]['text']


"""
class CoreAgent:
    def __init__(self, system_prompt, model_id='anthropic.claude-3-haiku-20240307-v1:0', region_name='us-west-2'):
        self.model_id = model_id
        self.system_prompt = [{"text": system_prompt}]
        self.brt = boto3.client(service_name='bedrock-runtime', region_name=region_name)

    def query(self, input_str):
        user_message = {"role": "user", "content": [{"text": input_str}]}
        messages = [user_message]
        FAILURE_COUNTER = 0

        while True:
            try:
                response = self.brt.converse(
                    modelId=self.model_id,
                    messages=messages,
                    system=self.system_prompt,
                )
                break
            except Exception as e:
                FAILURE_COUNTER += 1
                if FAILURE_COUNTER >= 5:
                    return "Error: Failed to get a response after multiple attempts."
                print(f'Exception encountered: {e}. Retrying in 60 seconds...')
                time.sleep(60)

        llm_response = response['output']['message']['content'][0]['text']
        return llm_response
"""


# def transform_to_gemini(messages_openai_style, sys_prompt=''):
#     messages_gemini = []
    
#     for message in messages_openai_style:
#         if message['role'] == 'system':
#             sys_prompt = message['content']
#         elif message['role'] == 'user':
#             messages_gemini.append({'role': 'user', 'parts': [message['content']]})
#         elif message['role'] == 'assistant':
#             messages_gemini.append({'role': 'model', 'parts': [message['content']]})
    
#     if sys_prompt and messages_gemini:
#         messages_gemini[0]['parts'].insert(0, f"[SYS]\n{sys_prompt}\n[/SYS]\n")
    
#     return messages_gemini


class CoreAgent:
    def __init__(self, system_prompt, model_id='anthropic.claude-3-haiku-20240307-v1:0', region_name='us-west-2'):
        self.model_id = model_id
        self.system_prompt = system_prompt
        if 'gpt' in self.model_id:
            self.openai_client = openai.OpenAI()
        elif 'gemini' in self.model_id:
            self.gemini_client = genai.GenerativeModel(
                model_name=self.model_id,
                system_instruction=self.system_prompt
            )
        else:
            self.brt = boto3.client(service_name='bedrock-runtime', region_name=region_name)

    def query(self, input_str):
        user_message = {"role": "user", "content": [{"text": input_str}]}
        messages = [user_message]
        FAILURE_COUNTER = 0

        while True:
            try:
                if 'gpt' in self.model_id:
                    completion = self.openai_client.chat.completions.create(
                        model=self.model_id,
                        messages=[
                            {"role": "system", "content": self.system_prompt},
                            {
                                "role": "user",
                                "content": input_str
                            }
                        ]
                    )
                    llm_response = completion.choices[0].message.content
                elif 'gemini' in self.model_id:
                    # messages = transform_to_gemini([
                    #         {"role": "system", "content": self.system_prompt},
                    #         {
                    #             "role": "user",
                    #             "content": input_str
                    #         }
                    #     ])
                    # print(messages)
                    messages = [input_str]
                    response = self.gemini_client.generate_content(messages)
                    llm_response = response._result.candidates[0].content.parts[0].text
                else:
                    response = self.brt.converse(
                        modelId=self.model_id,
                        messages=messages,
                        system=[{"text": self.system_prompt}],
                    )
                    llm_response = response['output']['message']['content'][0]['text']

                break

            except Exception as e:
                FAILURE_COUNTER += 1
                if FAILURE_COUNTER >= 5:
                    return "Error: Failed to get a response after multiple attempts."
                print(f'Exception encountered: {e}. Retrying in 60 seconds...')
                time.sleep(60)

        # llm_response = response['output']['message']['content'][0]['text']
        return llm_response





"""
import streamlit as st
import openai

client = openai.OpenAI()


def generate_response(prompt):
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    return completion.choices[0].message.content

# Streamlit app
st.title("GPT-4o Mini Chatbot")

user_input = st.text_input("You: ", "")

if st.button("Send"):
    if user_input:
        response = generate_response(user_input)
        st.text_area("GPT-4o Mini:", response, height=200)
    else:
        st.warning("Please enter a message.")
"""


# Multiple-line commands
# draft_sys_prompt = """Generate bash script from README. Generate bash commands ONLY: ```bash``` block. You must use the following format to generate the content.
# multiple-line commands should be merged into a single line command.
# - Extract bash commands ONLY (```bash``` block) and fill in the closest command category.

drafter_sys_prompt = """Extract bash script from README.
- Must use the COMMANDS format below wrapped in a ```bash``` block and executable.
- Multiple-line commands should be merged into single line commands.
- Extract bash commands and fill in the closest command category.

<README>
[README CONTENT HERE]
</README>

# COMMANDS
```bash
#!/bin/bash
# Environment Setup / Requirement / Installation
[FILL EXTRACTED COMMANDS HERE]
# Data / Checkpoint / Weight Download (URL)
[FILL EXTRACTED COMMANDS HERE]
# Training
[FILL EXTRACTED COMMANDS HERE]
# Inference / Demonstration
[FILL EXTRACTED COMMANDS HERE]
# Testing / Evaluation
[FILL EXTRACTED COMMANDS HERE]
```
"""

drafter_query_template = """
<README>
```{readme}```
</README>

# COMMANDS
"""

class BashScriptDrafer(CoreAgent):
    def __init__(self, model_id):
        super().__init__(system_prompt=drafter_sys_prompt, model_id=model_id)

    def query(self, input_str):
        query_str = drafter_query_template.format(readme=input_str)
        return {
            'query': query_str,
            'response': super().query(query_str)
        }



ragger_sys_prompt = """Provided COMMAND, execution STDOUT, STDERR, RETURN_CODE.
- If the command failed, return command(s) to resolve the issue.
- If the command succeeded, return the command as it is.

BE BRIEF AND RETURN BASH COMMAND ONLY.

# COMMAND
[COMMAND CONTENT]

# STDOUT
[STDOUT CONTENT]

# STDERR
[STDERR CONTENT]

# RETURN_CODE
[RETURN CODE CONTENT]

# REFERENCE INFORMATION
[REFERENCE INFORMATION CONTENT]

# RETURN BASH
[BASH RETURNED SHOULD BE MERGED INTO ONE SINGLE LINE WRAPPED IN ```bash``` BLOCK]
```bash
[RETURN CONTENT HERE]
```
"""

ragger_query_template = """
# COMMAND
{command}

# STDOUT
{stdout}

# STDERR
{stderr}

# RETURN CODE
{return_code}

# REFERENCE INFORMATION
{issue_info}

# RETURN BASH
"""


class IssueRagger(CoreAgent):
    def __init__(self, model_id):
        super().__init__(system_prompt=ragger_sys_prompt, model_id=model_id)
        self.last_2048_tokens_lambda = lambda text: ''.join(re.findall(r'\S+|\s+', text)[-2048:]) # lambda text: text.split()[-2048:]


    def query(self, log):
        query_str = ragger_query_template.format(
            command=log['command'],
            stdout=self.last_2048_tokens_lambda(log['stdout']),
            stderr=self.last_2048_tokens_lambda(log['stderr']),
            return_code=log['return_code'],
            # tree_dir=self.last_2048_tokens_lambda(log['tree_dir']),
            issue_info=log['issue_info']
        )
        return {
            'query': query_str,
            'response': super().query(query_str)
        }



analyzer_sys_prompt = """Provided COMMAND, execution STDOUT, STDERR, RETURN_CODE.
- If the command failed, return command(s) to resolve the issue.
- If the command succeeded, return the command as it is.

BE BRIEF AND RETURN BASH COMMAND ONLY.

# COMMAND
[COMMAND CONTENT]

# STDOUT
[STDOUT CONTENT]

# STDERR
[STDERR CONTENT]

# RETURN_CODE
[RETURN CODE CONTENT]

# DIR STRUCTURE
[DIRECTORY STRUCTURE CONTENT]

# RETURN BASH
[BASH RETURNED SHOULD BE MERGED INTO ONE SINGLE LINE WRAPPED IN ```bash``` BLOCK]
```bash
[RETURN CONTENT HERE]
```
"""

analyzer_query_template = """
# COMMAND
{command}

# STDOUT
{stdout}

# STDERR
{stderr}

# RETURN CODE
{return_code}

# DIR STRUCTURE
{tree_dir}

# RETURN BASH
"""


class LogAnalyzer(CoreAgent):
    def __init__(self, model_id):
        super().__init__(system_prompt=analyzer_sys_prompt, model_id=model_id)
        self.last_2048_tokens_lambda = lambda text: ''.join(re.findall(r'\S+|\s+', text)[-2048:]) # lambda text: text.split()[-2048:]


    def query(self, log):
        query_str = analyzer_query_template.format(
            command=log['command'],
            stdout=self.last_2048_tokens_lambda(log['stdout']),
            stderr=self.last_2048_tokens_lambda(log['stderr']),
            return_code=log['return_code'],
            tree_dir=self.last_2048_tokens_lambda(log['tree_dir']),
        )
        return {
            'query': query_str,
            'response': super().query(query_str)
        }




searcher_sys_prompt = """Provided COMMAND, execution STDOUT, STDERR and REFERENCE_FROM_WEB_SEARCH.

Return command(s) to resolve the issue.

BE BRIEF AND RETURN BASH COMMAND ONLY.

# COMMAND
[COMMAND CONTENT]

# STDOUT
[STDOUT CONTENT]

# STDERR
[STDERR CONTENT]

# REFERENCE_FROM_WEB_SEARCH
[REFERENCE_FROM_WEB_SEARCH CONTENT]

# RETURN BASH
[BASH RETURNED SHOULD BE MERGED INTO ONE SINGLE LINE WRAPPED IN ```bash``` BLOCK]
```bash
[RETURN CONTENT HERE]
```
"""

searcher_query_template = """
# COMMAND
{command}

# STDOUT
{stdout}

# STDERR
{stderr}

# REFERENCE_FROM_WEB_SEARCH
{reference_from_web_search}

# RETURN BASH
"""

search_termpalte = """# COMMAND
{command}

# STDOUT
{stdout}

# STDERR
{stderr}
"""

class WebSearcher(CoreAgent):
    def __init__(self, model_id):
        super().__init__(system_prompt=searcher_sys_prompt, model_id=model_id)
        self.last_1024_tokens_lambda = lambda text: ''.join(re.findall(r'\S+|\s+', text)[-1024:]) # lambda text: text.split()[-1024:]
        self.last_2048_tokens_lambda = lambda text: ''.join(re.findall(r'\S+|\s+', text)[-2048:]) # lambda text: text.split()[-2048:]
    
    def query(self, log):
        perplexity_query = search_termpalte.format(
            command=log['command'],
            stdout=self.last_1024_tokens_lambda(log['stdout']),
            stderr=self.last_1024_tokens_lambda(log['stderr']),
        )
        perplexity_response = perplexity_search(perplexity_query)
        query_str = searcher_query_template.format(
            command=log['command'],
            stdout=self.last_2048_tokens_lambda(log['stdout']),
            stderr=self.last_2048_tokens_lambda(log['stderr']),
            reference_from_web_search=perplexity_response
        )
        return {
            'perplexity_query': perplexity_query,
            'perplexity_response': perplexity_response,
            'query': query_str,
            'response': super().query(query_str)
        }

        # return super().query(
        #     searcher_query_template.format(
        #         command=log['command'],
        #         stdout=self.last_2048_tokens_lambda(log['stdout']),
        #         stderr=self.last_2048_tokens_lambda(log['stderr']),
        #         reference_from_web_search=reference_from_web_search,
        #         # tree_dir=self.last_2048_tokens_lambda(log['tree_dir']),
        #     )
        # )
