import os
import boto3
import json
from datetime import datetime
import time
from botocore.config import Config


def call_claude3(inputs, start, workload_size, model_id='anthropic.claude-3-haiku-20240307-v1:0'):
    config = Config(
        retries={
            'max_attempts': 10,
            'mode': 'adaptive'
        }
    )

    brt = boto3.client(service_name='bedrock-runtime',
                       region_name='us-west-2', config=config)
    results = []
    for i in range(start, min(start+workload_size, len(inputs))):
        input_prompt = inputs[i]['input']
        if input_prompt == 'missing':
            results.append((i, 'score: 0\n'))
            continue
        
        user_message = {"role": "user", "content": f"{input_prompt}"}
        messages = [user_message]
        max_tokens = 4096

        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                # "system": instruction,
                "messages": messages
            }
        )

        while True:
            try:
                response = brt.invoke_model(body=body, modelId=model_id)
                break
            except:
                print('exception in', start)
                time.sleep(70)
                continue

        response_body = json.loads(response.get('body').read())
        inputs[i]['command'] = response_body['content'][0]['text']
        inputs[i]['idx'] = i
        results.append(
            inputs[i]
        )

    end_time = datetime.now()
    return results

def inference(input):
    return call_claude3(inputs=[{
        'input': input}], start=0, workload_size=1)[0]['command']

class LLMAgent:
    def __init__(self, name='Agent', model_name='lmsys/vicuna-7b-v1.5'):
        self.name = name

    def query(self, prompt):
        response = inference(prompt)
        return response


class ProductManager(LLMAgent):
    def translate_description(self, user_description):
        prompt = f"As a product manager, translate the following user description into technical requirements:\n\nUser Description: {user_description}"
        response = self.query(prompt)
        print(f"{self.name} (Product Manager)\nQuery: {prompt}\nResponse: {response}\n")
        return response

class TechnologyLeader(LLMAgent):
    def decompose_task(self, technical_description):
        prompt = f"As a technology leader, decompose the following technical description into submodules and tasks:\n\nTechnical Description: {technical_description}"
        response = self.query(prompt)
        print(f"{self.name} (Technology Leader)\nQuery: {prompt}\nResponse: {response}\n")
        return response

class Programmer(LLMAgent):
    def write_code(self, task_description):
        prompt = f"As a programmer, write Python code for the following task:\n\nTask: {task_description}"
        response = self.query(prompt)
        print(f"{self.name} (Programmer)\nQuery: {prompt}\nResponse: {response}\n")
        return response

class Tester(LLMAgent):
    def verify_code(self, code, task_description):
        prompt = f"As a tester, write test cases in Python to verify the following code and ensure it meets the task description:\n\nCode: {code}\n\nTask Description: {task_description}"
        response = self.query(prompt)
        print(f"{self.name} (Tester)\nQuery: {prompt}\nResponse: {response}\n")
        return response

class MultiAgentSystem:
    def __init__(self, product_manager, technology_leader, programmers, testers):
        self.product_manager = product_manager
        self.technology_leader = technology_leader
        self.programmers = programmers
        self.testers = testers
    
    def run(self, user_description):
        # Product Manager translates user description into technical description
        technical_description = self.product_manager.translate_description(user_description)
        
        # Technology Leader decomposes task into submodules
        task_descriptions = self.technology_leader.decompose_task(technical_description)
        
        # Each Programmer writes code for a task
        task_list = task_descriptions.split('\n')
        code_snippets = []
        for i, task in enumerate(task_list):
            if task.strip():
                code = self.programmers[i % len(self.programmers)].write_code(task)
                code_snippets.append((task, code))
        
        # Each Tester verifies the code
        tests = []
        for i, (task, code) in enumerate(code_snippets):
            test_cases = self.testers[i % len(self.testers)].verify_code(code, task)
            tests.append((code, test_cases))
        
        self.integrate_code_and_tests(code_snippets, tests)
    
    def integrate_code_and_tests(self, code_snippets, tests):
        repo_name = "project_repo"
        os.makedirs(repo_name, exist_ok=True)
        
        with open(f"{repo_name}/README.md", "w") as readme_file:
            readme_file.write("# Project Repository\n\nThis repository contains the code and tests for the project.\n")
        
        for i, (task, code) in enumerate(code_snippets):
            file_path = f"{repo_name}/module_{i+1}.py"
            with open(file_path, "w") as code_file:
                code_file.write(code)
        
        with open(f"{repo_name}/test_code.py", "w") as test_file:
            for _, test_cases in tests:
                test_file.write(test_cases + "\n")
        
        print(f"Code and tests have been integrated into the {repo_name} directory.")

if __name__ == "__main__":
    product_manager = ProductManager(name='Alice')
    technology_leader = TechnologyLeader(name='Bob')
    programmers = [Programmer(name=f'Programmer {i+1}') for i in range(2)]  # Add more programmers as needed
    testers = [Tester(name=f'Tester {i+1}') for i in range(2)]  # Add more testers as needed

    system = MultiAgentSystem(product_manager, technology_leader, programmers, testers)
    
    user_description = input("Describe the project you want to implement: ")
    system.run(user_description)
