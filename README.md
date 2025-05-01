# CSR-Bench Repository

## Overview

The `csr-bench` repository provides a benchmarking and retrieval system with utilities for executing bash commands, interacting with models, and web searching. This repository is organized into several Python scripts that serve various functions, such as data retrieval, bash utilities, and model execution. 

For more details, please check our NAACL 2025 paper [CSR-Bench: Benchmarking LLM Agents in Deployment of
Computer Science Research Repositories](https://aclanthology.org/2025.naacl-long.633.pdf)

## Repository Structure

- **`main.py`**: The entry point of the repository where the core functionality is implemented.
- **`docker_setup.sh`**: A shell script to set up the environment and conduct experiments using Docker.
- **`requirements.txt`**: A list of Python dependencies required to run the project.
- **`csr/`**: The main module directory containing various Python utilities:
    - `bash_utils.py`: Functions related to executing and handling bash commands.
    - `retriever.py`: Handles data and information retrieval from Github Issues.
    - `model.py`: Manages machine learning model-related operations.
    - `dataloader.py`: Contains utilities for loading and managing datasets.
    - `editor.py`: Utility for editing data or files.
    - `web_search.py`: Implements web searching capabilities.
    - `utils.py`: Helper functions used throughout the project.
    - `const.py`: Constants and configuration used across modules.

## Prerequisites

To set up and run the repository, ensure the following prerequisites are met:

1. **Python 3.x**: Ensure you have Python 3 installed. You can download it from [here](https://www.python.org/downloads/).
2. **Docker (Optional)**: If you wish to use Docker for a containerized environment, ensure Docker is installed.
   - Follow instructions [here](https://docs.docker.com/get-docker/) to install Docker.

## Installation

1. Clone the repository to your local machine:

```bash
git clone <repository_url>
cd git-bench-main
```

2. Install the required Python dependencies using `pip`:

```bash
pip install -r requirements.txt
```

3. (Optional) Set up Docker if you'd prefer to run the environment in a containerized setup:

```bash
bash docker_setup.sh
```

## Usage

The primary script to run the system is `main.py`. You can execute it directly via the command line:

```bash
python main.py
```

### Bash Utilities

The `csr/bash_utils.py` module provides a set of utilities to execute and interact with bash commands programmatically. To use this, import the necessary functions into your script:

```python
from csr.bash_utils import your_function_here
```


### Model Operations

The `csr/model.py` provides functions for loading, evaluating, or interacting with machine learning models. Example:

```python
from csr.model import run_model

model_results = run_model(model_input)
```
