# ArgoAgent

A command-line interface for interacting with [Argo](https://argo.anl.gov/). Note that ArgoAgent uses Argo API and you need to be connected to the ANL network to use it.

## Features

- Send prompts to the Argo API along with the content of a single or multiple files.
- Modular system prompts for different use cases (see below)
- Predefined tasks with system prompts and user prompts (see below)
- Rich terminal output with markdown formatting and progress indicators
- Detailed logging and automated storing of the interactions
- Support for various file formats:
  - Text files (txt, csv, json, etc.)
  - PDF documents
  - Word documents (DOCX)
  - Excel spreadsheets (XLSX, XLS)
  - PowerPoint presentations (PPTX, PPT)
  - Markdown files
  - Source code files (py, js, java, etc.)
  - Configuration files (yaml, toml, etc.)

## Installation

```bash
# Install in development mode with all dependencies
pip install -e ".[dev]"

# Install with only required dependencies
pip install -e .

# Enable tab completion for bash
eval "$(register-python-argcomplete argoagent)"
# Add the above line to your ~/.bashrc to make it permanent
```

## Usage

```bash
# Basic usage
argoagent "Your prompt here"

# Using a system prompt
argoagent "Your prompt here" -s code_review -c code.py

# Using a predefined task
argoagent -t code_review -c code.py

# Using context from a file
argoagent "Summarize this" -c paper.pdf

# Using context from multiple files
argoagent "Compare these files" -c file1.txt file2.txt

# Using context from a directory
argoagent "Analyze this codebase" -c path/to/directory

# Using wildcard patterns
argoagent "Suggest improvement for the python code" -c "*.py"

# Using a prompt from a file
argoagent -p prompt.txt

# Counting tokens without making an API request
argoagent "Your prompt here" -n

# Using verbose logging
argoagent "Your prompt here" -v
```

## Tab Completion

ArgoAgent includes tab completion for command-line arguments, making it easier to use:

- Press TAB to complete file paths for the `-c/--context` option
- Press TAB to see available system prompts for the `-s/--system` option
- Press TAB to see available tasks for the `-t/--task` option

To enable tab completion permanently, add the following line to your `~/.bashrc` file:

```bash
eval "$(register-python-argcomplete argoagent)"
```

## Command-line Options

- `prompt`: The prompt to send to the model (positional argument)
- `-p, --prompt_file`: Path to a file containing the prompt
- `-c, --context`: Path(s) to file(s), directory(ies), or wildcard pattern(s) containing context
- `-s, --system`: System prompt to use (see available options below)
- `-t, --task`: Task to use (see available options below)
- `-u, --argo_url`: ARGO API endpoint URL
- `-a, --argo_user`: User for the Argo API request
- `-m, --model`: Model to use for the prompt
- `-temp, --temperature`: Sampling temperature (0-2)
- `-o, --top_p`: Top-p sampling (0-1)
- `-x, --max_tokens`: Maximum number of tokens in the response
- `-n, --number_of_tokens`: Only count and display the number of tokens
- `-v, --verbose`: Enable verbose logging

## Available System Prompts

ArgoAgent includes a modular system prompts framework that allows for easy extension and customization. Each prompt is stored as a separate markdown file in the `system_prompts` directory, making it easy to edit, version control, and extend.

### Built-in System Prompts

- `code_review`: For reviewing code and suggesting improvements
- `linux_help`: For getting help with Linux commands
- `linux_quick`: For quick Linux command suggestions without explanations
- `debug`: For debugging code issues
- `doc`: For generating documentation
- `text_summary`: For summarizing text content
- `markdown_expert`: For formatting content in markdown
- `security`: For security analysis and recommendations
- `performance`: For performance optimization
- `testing`: For creating test cases

### Adding Custom System Prompts

You can add your own system prompts by creating a new markdown file in the `system_prompts` directory. The file name (without the `.md` extension) will be used as the prompt name.

Example: To add a custom prompt for data analysis, create a file `system_prompts/data_analysis.md` with your prompt content.

## Available Tasks

ArgoAgent includes a task framework that combines system prompts with predefined user prompts. Each task is stored as a YAML file in the `tasks` directory.

### Built-in Tasks

- `code_review`: Review code for quality, bugs, and improvements
- `documentation`: Generate documentation for code
- `linux_command`: Get help with Linux commands
- `linux_quick_command`: Get quick Linux command suggestions
- `debug`: Debug code issues
- `document_summary`: Summarize the content of a document

### Adding Custom Tasks

You can add your own tasks by creating a new YAML file in the `tasks` directory. The file name (without the `.yaml` extension) will be used as the task name.

Example task file (`tasks/custom_task.yaml`):
```yaml
name: Custom Task
description: Description of the task
goal: The goal of the task
system_prompt: system_prompt_name
user_prompt: "The user prompt to use for this task"
```

## Environment Variables

You can set these environment variables to avoid specifying them in every command:

```bash
export ARGO_URL="your_api_url"
export ARGO_USER="your_username"
```

## Dependencies

### Required Dependencies
- requests>=2.31.0 (for API requests)
- tiktoken>=0.5.2 (for token counting)
- rich>=13.7.0 (for terminal formatting)
- PyMuPDF>=1.23.8 (for PDF handling)
- python-docx>=1.0.1 (for DOCX handling)
- openpyxl>=3.1.2 (for Excel handling)
- python-pptx>=0.6.23 (for PowerPoint handling)
- markdown>=3.5.1 (for Markdown handling)
- PyYAML>=6.0.1 (for task configuration)
- argcomplete>=3.2.2 (for tab completion)

### Development Dependencies
- ruff>=0.11.5 (for linting and formatting)
- pytest>=7.4.3 (for testing)
- black>=23.11.0 (for code formatting)
- isort>=5.12.0 (for import sorting)
- mypy>=1.7.1 (for type checking)
- pylint>=3.0.2 (for code analysis)

## Examples

### Code Review
```bash
argoagent "Review this code" -c path/to/code.py -s code_review
# Or using the task
argoagent -t code_review -c path/to/code.py
```

### Linux Command Help
```bash
argoagent "How do I find all files modified in the last 7 days?" -s linux_quick
# Or using the task
argoagent -t linux_quick_command "How do I find all files modified in the last 7 days?"
```

### Document Analysis
```bash
argoagent "Summarize this document" -c document.pdf
# Or using the task
argoagent -t document_summary -c document.pdf
```

### Multiple File Analysis
```bash
argoagent "Compare these files" -c "*.py"
```

### Debugging Code
```bash
argoagent "Debug this error" -c error.log -s debug
# Or using the task
argoagent -t debug -c error.log
```

### Generating Documentation
```bash
argoagent "Generate documentation" -c source.py -s doc
# Or using the task
argoagent -t documentation -c source.py
```

### Performance Optimization
```bash
argoagent "Optimize this code" -c algorithm.py -s performance
```

### Security Analysis
```bash
argoagent "Check for security issues" -c web_app.py -s security
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
