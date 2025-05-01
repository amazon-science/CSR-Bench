# Given the name list, create name to model ID mapping
# Claude 3 Sonnet	1	anthropic.claude-3-sonnet-20240229-v1:0
# Claude 3.5 Sonnet	1	anthropic.claude-3-5-sonnet-20240620-v1:0
# Claude 3 Haiku	1	anthropic.claude-3-haiku-20240307-v1:0
# Claude 3 Opus	1	anthropic.claude-3-opus-20240229-v1:0
# Claude Instant	1.x	anthropic.claude-instant-v1
# Llama 2 Chat 13B	1.x	meta.llama2-13b-chat-v1
# Llama 2 Chat 70B	1.x	meta.llama2-70b-chat-v1
# Llama 3 8b Instruct	1.x	meta.llama3-8b-instruct-v1:0
# Llama 3 70b Instruct	1.x	meta.llama3-70b-instruct-v1:0
# Llama 3.1 8b Instruct	1.x	meta.llama3-1-8b-instruct-v1:0
# Llama 3.1 70b Instruct	1.x	meta.llama3-1-70b-instruct-v1:0
# Llama 3.1 405B Instruct	1.x	meta.llama3-1-405b-instruct-v1:0
# Mistral 7B Instruct	0.x	mistral.mistral-7b-instruct-v0:2
# Mixtral 8X7B Instruct	0.x	mistral.mixtral-8x7b-instruct-v0:1
# Mistral Large	1.x	mistral.mistral-large-2402-v1:0
# Mistral Large 2 (24.07)	1.x	mistral.mistral-large-2407-v1:0
# Mistral Small	1.x	mistral.mistral-small-2402-v1:0

# Anthropic	Claude 3 Sonnet	1	anthropic.claude-3-sonnet-20240229-v1:0
# Anthropic	Claude 3.5 Sonnet	1	anthropic.claude-3-5-sonnet-20240620-v1:0
# Anthropic	Claude 3 Haiku	1	anthropic.claude-3-haiku-20240307-v1:0
# Anthropic	Claude 3 Opus	1	anthropic.claude-3-opus-20240229-v1:0
# Anthropic	Claude Instant	1.x	anthropic.claude-instant-v1
# Meta	Llama 2 Chat 13B	1.x	meta.llama2-13b-chat-v1
# Meta	Llama 2 Chat 70B	1.x	meta.llama2-70b-chat-v1
# Meta	Llama 3 8b Instruct	1.x	meta.llama3-8b-instruct-v1:0
# Meta	Llama 3 70b Instruct	1.x	meta.llama3-70b-instruct-v1:0
# Meta	Llama 3.1 8b Instruct	1.x	meta.llama3-1-8b-instruct-v1:0
# Meta	Llama 3.1 70b Instruct	1.x	meta.llama3-1-70b-instruct-v1:0
# Meta	Llama 3.1 405B Instruct	1.x	meta.llama3-1-405b-instruct-v1:0
# Mistral AI	Mistral 7B Instruct	0.x	mistral.mistral-7b-instruct-v0:2
# Mistral AI	Mixtral 8X7B Instruct	0.x	mistral.mixtral-8x7b-instruct-v0:1
# Mistral AI	Mistral Large	1.x	mistral.mistral-large-2402-v1:0
# Mistral AI	Mistral Large 2	1.x	mistral.mistral-large-2407-v1:0
# Mistral AI	Mistral Small	1.x	mistral.mistral-small-2402-v1:0

NAME_TO_ID = {
    "Claude_3_Sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
    "Claude_3.5_Sonnet": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "Claude_3_Haiku": "anthropic.claude-3-haiku-20240307-v1:0",
    "Claude_3_Opus": "anthropic.claude-3-opus-20240229-v1:0",
    "Claude_Instant": "anthropic.claude-instant-v1",

    "Llama_2_Chat_13B": "meta.llama2-13b-chat-v1",
    "Llama_2_Chat_70B": "meta.llama2-70b-chat-v1",

    "Llama_3_8b_Instruct": "meta.llama3-8b-instruct-v1:0",
    "Llama_3_70b_Instruct": "meta.llama3-70b-instruct-v1:0",

    "Llama_3.1_8b_Instruct": "meta.llama3-1-8b-instruct-v1:0",
    "Llama_3.1_70b_Instruct": "meta.llama3-1-70b-instruct-v1:0",
    "Llama_3.1_405B_Instruct": "meta.llama3-1-405b-instruct-v1:0",

    "Mistral_7B_Instruct": "mistral.mistral-7b-instruct-v0:2",
    "Mixtral_8X7B_Instruct": "mistral.mixtral-8x7b-instruct-v0:1",
    "Mistral_Large": "mistral.mistral-large-2402-v1:0",
    "Mistral_Large_2": "mistral.mistral-large-2407-v1:0",
    "Mistral_Small": "mistral.mistral-small-2402-v1:0",
    # gpt-4o gpt-4o-mini gpt-4-turbo
    "GPT_4o": "gpt-4o",
    "GPT_4o_Mini": "gpt-4o-mini",
    "GPT_4_Turbo": "gpt-4-turbo",
    "Gemini_1.5_Flash": "gemini-1.5-flash",
    "Gemini_1.5_Pro": "gemini-1.5-pro",
}

ERR_MSG = "[AGENT_ERROR]"

instruction = """Generate bash script to from the README. Generate bash commands ONLY: ```bash``` block. You must use the following format to generate the content.

## README
README CONTENT HERE.

## COMMANDS
```bash
#!/bin/bash
### Environment Setup / Requirement / Installation
[FILL EXTRACTED COMMANDS HERE]

### Data / Checkpoint / Weight Download (URL)
[FILL EXTRACTED COMMANDS HERE]

### Training
[FILL EXTRACTED COMMANDS HERE]

### Inference / Demonstration
[FILL EXTRACTED COMMANDS HERE]

### Testing / Evaluation
[FILL EXTRACTED COMMANDS HERE]
```
"""


input_template = """
## README
```{readme}```

## COMMANDS
"""


category_instruction = """Provided the README of a GitHub repository, determine if the repository is in preferred format [generally for research topics with instructions about set up, variations are allowed].

```Markdown
README example:
# Environment Setup / Requirement / Installation
...
# Data/Weight Download (URL)
...
# Usage (training, inference)
...
# Results [Optional]
```

Answer with "YES" or "NO" based on the provided README.
"""


category_input_template = """
[README]
```Markdown
{readme}
```

Analysis: [reasons for each scoring and answer about whether this README is preferred or not.]
Answer: [YES or NO]
"""




prepend_str = """#!/bin/bash

apt-get update
apt-get install bc

# Initialize counters
total_steps=0
successful_steps=0

# Function to execute a command and check for success
execute_step() {
    echo "Executing: $1"
    if bash -c "$1"; then
        echo "Success: $1"
        ((successful_steps++))
    else
        echo "Failed: $1, skipping..."
    fi
    ((total_steps++))
}

"""


sample_readme = """# MLP with PyTorch

This repository contains a simple implementation of a Multi-Layer Perceptron (MLP) model using PyTorch.

# Environment Setup / Requirement / Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/MLP_PyTorch.git
    cd MLP_PyTorch
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

# Data / Checkpoint / Weight Download (URL)

1. Download the dataset:
    ```bash
    python data/download_data.py
    ```

2. (Optional) Download pre-trained weights (if available) from [here](URL_TO_CHECKPOINT).

# Training

To train the MLP model, run the following command:
```bash
python train.py --epochs 50 --batch_size 32 --learning_rate 0.001
```

# Inference / Demonstration

To perform inference using the trained model, run:
```bash
python inference.py --input "path_to_input_data"
```

# Testing / Evaluation

To evaluate the model on the test dataset, run:
```bash
python inference.py --input "path_to_input_data"
```
"""

append_str = """
# Log total and successful steps
echo "Total steps: $total_steps"
echo "Successful steps: $successful_steps"
"""
