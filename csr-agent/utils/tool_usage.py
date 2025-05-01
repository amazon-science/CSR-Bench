import json
import logging
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

from csr.perplexity import pplx


class ToolAgent:
    def __init__(self, model_id, tool_config, region_name='us-west-2', max_attempts=3, adaptive_mode='adaptive'):
        self.model_id = model_id
        self.tool_config = tool_config
        self.config = Config(
            retries={
                'max_attempts': max_attempts,
                'mode': adaptive_mode
            }
        )
        self.bedrock_client = boto3.client(service_name='bedrock-runtime', region_name=region_name, config=self.config)
        self.logger = logging.getLogger(__name__)
        # self.tools = dict()
        logging.basicConfig(level=logging.INFO)


    def pplx(self, message):
        return pplx(message)

    def generate_text(self, input_text):
        """Generates text using the supplied Amazon Bedrock model."""
        self.logger.info("Generating text with model %s", self.model_id)
        messages = [{"role": "user", "content": [{"text": input_text}]}]
        response = self.bedrock_client.converse(
            modelId=self.model_id,
            messages=messages,
            toolConfig=self.tool_config
        )

        output_message = response['output']['message']
        messages.append(output_message)
        stop_reason = response['stopReason']

        if stop_reason == 'tool_use':
            tool_requests = output_message['content']
            for tool_request in tool_requests:
                if 'toolUse' in tool_request:
                    tool = tool_request['toolUse']
                    self.logger.info("Requesting tool %s. Request: %s", tool['name'], tool['toolUseId'])
                    try:
                        analysis = self.pplx(tool['input']['log_msg'])
                        tool_result = {"toolUseId": tool['toolUseId'], "content": [{"text": analysis}]}
                    except Exception as err:
                        tool_result = {"toolUseId": tool['toolUseId'], "content": [{"text": err.args[0]}], "status": 'error'}

                    tool_result_message = {"role": "user", "content": [{"toolResult": tool_result}]}
                    messages.append(tool_result_message)
                    response = self.bedrock_client.converse(
                        modelId=self.model_id,
                        messages=messages,
                        toolConfig=self.tool_config
                    )
                    output_message = response['output']['message']

        print(output_message['content'][0]['text'])


    def query(self, msg):
        try:
            self.generate_text(msg)
        except ClientError as err:
            message = err.response['Error']['Message']
            self.logger.error("A client error occurred: %s", message)
            print(f"A client error occurred: {message}")
        else:
            print(f"Finished generating text with model {self.model_id}")


if __name__ == "__main__":
    model_id = "cohere.command-r-v1:0"
    model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    tool_config = {
        "tools": [
            {
                "toolSpec": {
                    "name": "perplexity",
                    "description": "Search the web for solutions.",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "log_msg": {
                                    "type": "string",
                                    # module not found (pip, gcc, etc.)
                                    "description": "The log message to analyze. Examples messages are `import error: no module named numpy` and `error: command 'gcc' failed with exit status 1`."
                                    # The call sign for the radio station for which you want the most popular song. Example calls signs are WZPZ, and WKRP.
                                }
                            },
                            "required": [
                                "log_msg"
                            ]
                        }
                    }
                }
            }
        ]
    }

    agent = ToolAgent(model_id, tool_config)
    # agent.main()
    input_text = """>>> import esm
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ModuleNotFoundError: No module named 'esm'"""

    input_text = """gcc
gcc: fatal error: no input files
compilation terminated."""
    
    agent.query(input_text)

