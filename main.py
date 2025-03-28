import os
import re
import json
from gsr.model import BashScriptDrafer, LogAnalyzer, IssueRagger, WebSearcher
from gsr.utils import extract_commands, repo_structure
from gsr.bash_utils import CommandExecutor
from gsr.const import NAME_TO_ID
from colorama import Fore, Style, init
from gsr.retriever import RetrievalEngine
import google.generativeai as genai
import openai


genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Initialize Colorama
init(autoreset=True)

import argparse
parser = argparse.ArgumentParser(description='GSRBench100')

parser.add_argument('--repo', type=str, help='Repository name')

parser.add_argument('--model', type=str, choices=NAME_TO_ID.keys(), help='Model name')

args = parser.parse_args()
REPO_NAME = args.repo
MODEL_NAME = args.model
MODEL_ID = NAME_TO_ID[MODEL_NAME]

WORKING_DIR = f'/workspace/{REPO_NAME}/'

# REPO_NAME = '3DDFA_V2'
# WORKING_DIR = f'/home/yijia/{REPO_NAME}/'

README_PATH = f'{WORKING_DIR}/README.md' if os.path.exists(f'{WORKING_DIR}/README.md') else f'{WORKING_DIR}/readme.md'

MAX_ATTEMPTS = 3
MAX_ATTEMPTS = 2
DO_ANALYSIS = True
DO_RAG = True
DO_SEARCH = True


# TIMEOUT = 15
# TIMEOUT = 300
TIMEOUT = 300

SECTION_LIST = [
    '# Environment Setup / Requirement / Installation',
    '# Data / Checkpoint / Weight Download (URL)',
    '# Training',
    '# Inference / Demonstration',
    '# Testing / Evaluation'
]

def refine_cmd_extraction(log_analysis):
    pattern = r"```bash\n(.*?)\n```"
    matches = re.findall(pattern, log_analysis, re.DOTALL)
    # return ' && '.join([match.strip() for match in matches]) if matches else ""
    return (' && '.join([match.strip() for match in matches]) if matches else "").replace('\n',' && ')


# Ensure byte objects are converted to strings
def convert_bytes(data):
    if isinstance(data, bytes):
        return data.decode('utf-8')
    elif isinstance(data, dict):
        return {key: convert_bytes(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_bytes(item) for item in data]
    return data

tree_dir = repo_structure(WORKING_DIR)
print(tree_dir)

try:
    issue_retriever = RetrievalEngine(os.path.join(WORKING_DIR, f'{REPO_NAME}.json'))
except:
    issue_retriever = None
    DO_RAG = False


def atom_step(command, executor, analyzer, ragger, searcher, working_dir, DO_ANALYSIS, DO_RAG, DO_SEARCH, MAX_ATTEMPTS):
    # tree_dir = repo_structure(working_dir)
    
    print(Fore.LIGHTGREEN_EX + f"###### Initial Execution: {command}")
    
    execution_log = executor.execute_cmd(command, directory=working_dir)

    # Initialize results dictionary
    results = {
        'initial_execution': {
            'command': command,
            'stdout': execution_log['stdout'],
            'stderr': execution_log['stderr'],
            'return_code': execution_log['return_code'],
            'execution_log': execution_log
        },
        'with_analyzer': [],
        'with_ragger': [],
        'with_searcher': []
    }

    attempts = 0
    ANALYSIS_CODE = execution_log['return_code']

    if DO_ANALYSIS and ANALYSIS_CODE != 0:
        analyzer_command = command
        analyzer_log = execution_log
        while (ANALYSIS_CODE != 0) and attempts < MAX_ATTEMPTS:
            # print(Fore.RED + 'Handling failure', command)
            print(Fore.RED + 'Handling Analyzer Failure', analyzer_command)
            print(Fore.YELLOW + f"stdout: {analyzer_log['stdout']}")
            print(Fore.RED + f"stderr: {analyzer_log['stderr']}")

            query_log = {
                'command': analyzer_command,
                'stdout': analyzer_log['stdout'],
                'stderr': analyzer_log['stderr'],
                'return_code': analyzer_log['return_code'],
                'tree_dir': tree_dir,
            }

            analyzer_dict = analyzer.query(query_log)
            analyzer_response = analyzer_dict['response']
            print(Fore.CYAN + 'Log Analysis:', analyzer_response)

            analyzer_command = refine_cmd_extraction(analyzer_response)
            print(Fore.GREEN + 'Analyzer Command:', analyzer_command)

            analyzer_log = executor.execute_cmd(analyzer_command, directory=working_dir)

            print(Fore.YELLOW + f"stdout: {analyzer_log['stdout']}")
            print(Fore.RED + f"stderr: {analyzer_log['stderr']}")
            print(Fore.GREEN + f"return_code: {analyzer_log['return_code']}")

            results['with_analyzer'].append({
                'command': analyzer_command,
                'stdout': analyzer_log['stdout'],
                'stderr': analyzer_log['stderr'],
                'return_code': analyzer_log['return_code'],
                'analyzer_dict': analyzer_dict
            })
            ANALYSIS_CODE = analyzer_log['return_code']

            if ANALYSIS_CODE == 0:
                print(Fore.GREEN + "Issue resolved.")
                break

            attempts += 1

    attempts = 0
    RAG_CODE = ANALYSIS_CODE
    if DO_RAG and RAG_CODE != 0:
        rag_command = analyzer_command
        rag_log = analyzer_log
        while (RAG_CODE != 0) and attempts < MAX_ATTEMPTS:
            print(Fore.RED + 'Handling Ragger Failure', rag_command)
            print(Fore.YELLOW + f"stdout: {rag_log['stdout']}")
            print(Fore.RED + f"stderr: {rag_log['stderr']}")

            try:
                # retrieved_issues = issue_retriever.query(f"{rag_command}\n{execution_log['stdout']}\n{execution_log['stderr']}", top_k=3)
                retrieved_issues = issue_retriever.query(f"{rag_command}\n{rag_log['stdout']}\n{rag_log['stderr']}", top_k=3)
                issue_info = '\n'.join([f'<Issue Reference {i}>\n{issue}' for i, issue in enumerate(retrieved_issues)])
            except:
                issue_info = 'No information provided.'

            query_log = {
                'command': rag_command,
                'stdout': rag_log['stdout'],
                'stderr': rag_log['stderr'],
                'return_code': rag_log['return_code'],
                'issue_info': issue_info
            }

            ragger_dict = ragger.query(query_log)
            ragger_response = ragger_dict['response']
            
            print(Fore.MAGENTA + 'Issue Rag:', ragger_response)
            
            rag_command = refine_cmd_extraction(ragger_response)
            print(Fore.GREEN + 'Ragger Command:', rag_command)

            rag_log = executor.execute_cmd(rag_command, directory=working_dir)
            print(Fore.YELLOW + f"stdout: {rag_log['stdout']}")
            print(Fore.RED + f"stderr: {rag_log['stderr']}")
            print(Fore.GREEN + f"return_code: {rag_log['return_code']}")
            
            results['with_ragger'].append({
                'command': rag_command,
                'stdout': rag_log['stdout'],
                'stderr': rag_log['stderr'],
                'return_code': rag_log['return_code'],
                'ragger_dict': ragger_dict
            })
            
            # ###
            # rag_feedback_dict = ragger.query(log)
            # rag_feedback_response = rag_feedback_dict['response']
            # print(Fore.MAGENTA + 'Rag Feedback:', rag_feedback_response)

            # refined_command = refine_cmd_extraction(rag_feedback_response)
            # print(Fore.GREEN + 'Refined Command:', refined_command)

            # refined_execution_log = executor.execute_cmd(refined_command, directory=working_dir)
            # print(Fore.YELLOW + f"stdout: {refined_execution_log['stdout']}")
            # print(Fore.RED + f"stderr: {refined_execution_log['stderr']}")
            # print(Fore.GREEN + f"return_code: {refined_execution_log['return_code']}")

            # results['with_ragger'].append({
            #     'command': refined_command,
            #     'stdout': refined_execution_log['stdout'],
            #     'stderr': refined_execution_log['stderr'],
            #     'return_code': refined_execution_log['return_code'],
            #     'rag_feedback_dict': rag_feedback_dict
            # })

            # RAG_CODE = refined_execution_log['return_code']
            RAG_CODE = rag_log['return_code']
            if RAG_CODE == 0:
                print(Fore.GREEN + "Issue resolved.")
                break

            attempts += 1

    attempts = 0
    SEARCH_CODE = RAG_CODE

    if DO_SEARCH and SEARCH_CODE != 0:
        search_command = rag_command
        search_log = rag_log
        while (SEARCH_CODE != 0) and attempts < MAX_ATTEMPTS:
            print(Fore.RED + 'Handling Searcher Failure', search_command)
            print(Fore.YELLOW + f"stdout: {search_log['stdout']}")
            print(Fore.RED + f"stderr: {search_log['stderr']}")

            query_log = {
                'command': search_command,
                'stdout': search_log['stdout'],
                'stderr': search_log['stderr'],
                'return_code': search_log['return_code'],
                'tree_dir': tree_dir
            }
            
            # web_feedback_dict = searcher.query(query_log)
            searcher_dict = searcher.query(query_log)
            # web_feedback_response = web_feedback_dict['response']
            searcher_response = searcher_dict['response']

            print(Fore.BLUE + 'Web Search:', searcher_response)

            # refined_command = refine_cmd_extraction(web_feedback_response)
            search_command = refine_cmd_extraction(searcher_response)
            # print(Fore.GREEN + 'Refined Command:', refined_command)
            print(Fore.GREEN + 'Searcher Command:', search_command)

            # refined_execution_log = executor.execute_cmd(refined_command, directory=working_dir)
            searcher_log = executor.execute_cmd(search_command, directory=working_dir)
            print(Fore.YELLOW + f"stdout: {searcher_log['stdout']}")
            print(Fore.RED + f"stderr: {searcher_log['stderr']}")
            print(Fore.GREEN + f"return_code: {searcher_log['return_code']}")

            results['with_searcher'].append({
                'command': search_command,
                'stdout': searcher_log['stdout'],
                'stderr': searcher_log['stderr'],
                'return_code': searcher_log['return_code'],
                'searcher_dict': searcher_dict
            })

            SEARCH_CODE = searcher_log['return_code']
            if SEARCH_CODE == 0:
                print(Fore.GREEN + "Issue resolved.")
                break

            attempts += 1

    return results


executor = CommandExecutor(timeout=TIMEOUT, model_id=MODEL_ID)
drafter = BashScriptDrafer(model_id=MODEL_ID)
analyzer = LogAnalyzer(model_id=MODEL_ID)
ragger = IssueRagger(model_id=MODEL_ID)
searcher = WebSearcher(model_id=MODEL_ID)

with open(README_PATH, 'r') as file:
    readme_content = file.read()

draft_dict = drafter.query(readme_content)
draft_response = draft_dict['response']
command_dict = extract_commands(draft_response)
print(command_dict)

result_dict = {}

for section, section_commands in command_dict.items():
    print(Fore.CYAN + f"Analyzing Section: {section}")
    result_dict[section] = []
    for command in section_commands:
        result = atom_step(command, executor, analyzer, ragger, searcher, WORKING_DIR, DO_ANALYSIS, DO_RAG, DO_SEARCH, MAX_ATTEMPTS)
        result_dict[section].append(result)

# Convert result before saving
result_dict = convert_bytes(result_dict)

# Save results using REPO_NAME as the filename
with open(f'/workspace/results/{MODEL_NAME}-{REPO_NAME}.json', 'w') as f:
# with open(f'./assets/{MODEL_NAME}-{REPO_NAME}.json', 'w') as f:
    json.dump(result_dict, f, indent=4)
