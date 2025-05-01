import os
import re
import subprocess

def extract_commands(script):
    # If script start with ```bash [end with ```], then extract the content using regex
    # Example: script = re.findall(r'#!/bin/bash\n(.*?)\n```', script, re.DOTALL)
    script = '\n'.join(re.findall(r'```bash\n(.*?)\n```', script, re.DOTALL))

    # Define category headers
    categories = {
        "# Environment Setup / Requirement / Installation": [],
        "# Data / Checkpoint / Weight Download (URL)": [],
        "# Training": [],
        "# Inference / Demonstration": [],
        "# Testing / Evaluation": []
    }
    
    # Current category
    current_category = None
    
    # Split the script into lines
    lines = script.split('\n')
    
    # Iterate over each line
    for line in lines:
        # Check if the line is a category header
        if line.strip() in categories:
            current_category = line.strip()
        elif current_category and line.strip() and not line.startswith('#'):
            # Add the line to the current category if it's not a comment or empty
            categories[current_category].append(line.strip())
    
    return categories


def execute_cmd(command, directory=None, timeout=600):
    print('Executing command:', command, 'in directory:', directory, 'with timeout:', timeout, 'seconds')
    """
    Execute a system command in a specified directory with a maximum execution time.

    Parameters:
    command (str): The command to be executed.
    directory (str, optional): The directory in which to execute the command. Defaults to None.
    timeout (int, optional): The maximum execution time for the command in seconds. Defaults to 600.

    Returns:
    tuple: A tuple containing the standard output, standard error, and the return code from the executed command.
    """

    try:
        # Run the command in the specified directory and capture the output and error
        result = subprocess.run(f'/bin/bash -c "{command}"', shell=True, text=True, capture_output=True, cwd=directory, timeout=timeout)
        
        # Get the standard output
        stdout = result.stdout
        # Get the standard error
        stderr = result.stderr
        # Get the return code
        return_code = result.returncode

    except subprocess.TimeoutExpired as e:
        stdout = e.stdout if e.stdout else ""
        stderr = e.stderr if e.stderr else f'The command timed out after {timeout} seconds'
        return_code = -999  # Specific code for timeout

    return stdout, stderr, return_code



def handle_failure(command, directory):
    print(f"Error executing command: {command}")
    print("Please input a command to resolve the issue or type 'skip' to continue:")
    while True:
        user_command = input("Enter command: ")
        if user_command.lower() == 'skip':
            break
        stdout, stderr, return_code = execute_cmd(user_command, directory=directory)
        print(f"Command: {user_command}")
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")
        print(f"return_code: {return_code}")
        # if return_code == 0:
        # If command executed successfully, break the loop
        if execute_cmd(command, directory=directory)[2] == 0:
            print("Issue resolved.")
            break
        else:
            print("Error persists. Please try another command or type 'skip' to continue.")


def repo_structure(dir_path, level=0):
    # Ensure the directory exists
    if not os.path.exists(dir_path):
        return "Directory does not exist: " + dir_path

    # List all files and directories in the current directory
    entries = [entry for entry in os.listdir(dir_path) if not entry.startswith('.')]
    entries.sort()
    
    # Initialize an empty list to collect directory structure strings
    dir_structure = []
    
    # Prefix that increases with each level of depth
    prefix = '  ' * level
    
    for entry in entries:
        # Current path for the entry
        current_path = os.path.join(dir_path, entry)
        
        # Check if the current entry is a directory
        if os.path.isdir(current_path):
            # Recursively get the structure of the subdirectory
            sub_dir = repo_structure(current_path, level + 1)
            # Add current directory and its substructure to the list
            dir_structure.append(f'{prefix}- {entry}/:\n{sub_dir}')
        else:
            # Just add the file name
            dir_structure.append(f'{prefix}- {entry}')
    
    # Join all parts of the directory structure into a single string
    return '\n'.join(dir_structure)

