import pexpect
import re
from csr.model import CoreAgent


sys_prompt = """Given the execution output, decide if the command is successful or not.

**Answer with 'YES' or 'NO' only.**

# COMMAND
[COMMAND CONTENT]

# STDOUT
[STDOUT CONTENT]

# STDERR
[STDERR CONTENT]

# RETURN_CODE
[RETURN CODE CONTENT]
"""

query_template = """
# COMMAND
{command}

# STDOUT
{stdout}

# STDERR
{stderr}

# RETURN CODE
"""

class ExecutionParser(CoreAgent):
    def __init__(self, model_id):
        super().__init__(system_prompt=sys_prompt, model_id=model_id)

    def query(self, command, stdout_output, stderr_output):
        query_str = query_template.format(
            command=command,
            stdout=stdout_output,
            stderr=stderr_output
        )
        return {
            'query': query_str,
            'response': super().query(query_str)
        }


class CommandExecutor:
    def __init__(self, timeout=900, model_id='anthropic.claude-3-haiku-20240307-v1:0'):
        # Initialize the pexpect child process
        self.child = pexpect.spawn('/bin/bash', encoding='utf-8', timeout=timeout, echo=False)
        self.set_prompt()
        self.parser = ExecutionParser(model_id=model_id)

    def set_prompt(self):
        # Set a unique prompt to ensure clear command boundaries
        unique_prompt = 'CMD_EXECUTOR_PROMPT>'
        self.child.sendline(f'export PS1="{unique_prompt}"')
        self.child.expect(unique_prompt)

    def execute_cmd(self, command, directory=None):
        command = ' && '.join(line.strip().replace('\\', ' ') for line in command.splitlines())
        stdout_file = '/tmp/cmd_stdout.txt'
        stderr_file = '/tmp/cmd_stderr.txt'
        # Create empty files to store stdout and stderr
        open(stdout_file, 'w').close()
        open(stderr_file, 'w').close()

        # if directory:
        #     # Change to the specified directory
        #     self.child.sendline(f'cd "{directory}"')
        #     self.child.expect('CMD_EXECUTOR_PROMPT>')

        def read_std():
            with open(stdout_file, 'r') as file:
                stdout_output = file.read().strip()
            with open(stderr_file, 'r') as file:
                stderr_output = file.read().strip()
            return stdout_output.replace("\x00", ""), stderr_output.replace("\x00", "")

        try:
            if directory:
                # Change to the specified directory
                self.child.sendline(f'cd "{directory}"')
                self.child.expect('CMD_EXECUTOR_PROMPT>')

            # Execute the command with stdout and stderr directed to respective files
            self.child.sendline(f'{command} >{stdout_file} 2>{stderr_file}; echo Return code: $?')
            # Wait for the command to complete and capture the output including the exit code
            self.child.expect('CMD_EXECUTOR_PROMPT>')
            
            # Read stdout and stderr from their respective files
            # Handle exceptions if the files are not found (set to empty strings)

            """
            with open(stdout_file, 'r') as file:
                stdout_output = file.read().strip()
            with open(stderr_file, 'r') as file:
                stderr_output = file.read().strip()
            """
            stdout_output, stderr_output = read_std()

            # Extract the return code from the last line of the output
            # command_output = self.child.before.strip()
            # match = re.search(r'Return code: (\d+)', command_output)
            # return_code = int(match.group(1)) if match else None
            return_code_log = self.parser.query(command, stdout_output, stderr_output)
            print(return_code_log)
            return_code_str = return_code_log['response']
            return_code = 0 if 'YES' in return_code_str else 1

            return {
                "stdout": stdout_output,
                "stderr": stderr_output,
                "return_code": return_code
            }

        except pexpect.exceptions.TIMEOUT:
            # Handle the timeout scenario
            """
            with open(stdout_file, 'r') as file:
                stdout_output = file.read().strip()
            with open(stderr_file, 'r') as file:
                stderr_output = file.read().strip()
            """
            stdout_output, stderr_output = read_std()

            return {
                "stdout": stdout_output,
                "stderr": stderr_output + "\nCommand timed out",
                "return_code": 124  # timeout exit code
            }
        
        except pexpect.exceptions.EOF:
            """
            with open(stdout_file, 'r') as file:
                stdout_output = file.read().strip()
            with open(stderr_file, 'r') as file:
                stderr_output = file.read().strip()
            """
            stdout_output, stderr_output = read_std()

            return {
                "stdout": stdout_output,
                "stderr": stderr_output + "\nEOF",
                "return_code": 1
            }
        
        except Exception as e:
            """
            with open(stdout_file, 'r') as file:
                stdout_output = file.read().strip()
            with open(stderr_file, 'r') as file:
                stderr_output = file.read().strip()
            """
            stdout_output, stderr_output = read_std()

            return {
                "stdout": stdout_output,
                "stderr": stderr_output + "\n" + str(e),
                "return_code": 1
            }

    def close(self):
        # Ensure the child process is properly terminated
        self.child.sendline('exit')
        self.child.close()


if __name__ == "__main__":
    # Example usage
    executor = CommandExecutor(timeout=30)

    # Assuming you need to activate an environment
    execution_ret = executor.execute_cmd('python -m venv venv', directory='./data/csr_data/Repo/')
    # print(execution_ret)

    # Execute commands in the activated environment
    execution_ret = executor.execute_cmd('source venv/bin/activate', directory='./data/csr_data/Repo/')
    # print(execution_ret)

    # Optionally execute a command in a specific directory
    execution_ret = executor.execute_cmd('pip install -r requirements.txt', directory='./data/csr_data/Repo/')
    # print(execution_ret)

    execution_ret = executor.execute_cmd('which pip', directory='./data/csr_data/Repo/')
    # print(execution_ret)

    execution_ret = executor.execute_cmd('ABCBACBAC', directory='./data/csr_data/Repo/')
    # print(execution_ret)


    # Create a loop and prompt the user for commands
    while True:
        command = input('Enter a command to execute (or "exit" to quit): ')
        if command.lower() == 'exit':
            break
        execution_ret = executor.execute_cmd(command)
        print(execution_ret)

    # Close the session when done
    executor.close()

