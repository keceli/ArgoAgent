# ArgoAgent

A command-line interface for interacting with the Argo API, providing a simple way to send prompts and receive responses from various language models.

## Features

- Send prompts to the Argo API and receive responses
- Support for multiple language models (GPT-4, GPT-3.5, etc.)
- Context-aware prompts with file and directory support
- System prompts for different use cases
- Token counting and validation
- Rich terminal output with markdown formatting
- Progress indicators for API requests
- Comprehensive logging
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
```

## Usage

```bash
# Basic usage
argoagent "Your prompt here"

# Using a system prompt
argoagent "Your prompt here" -s code_review

# Using context from a file
argoagent "Summarize this" -c path/to/file.txt

# Using context from multiple files
argoagent "Compare these files" -c file1.txt file2.txt

# Using context from a directory
argoagent "Analyze this codebase" -c path/to/directory

# Using wildcard patterns
argoagent "Find patterns" -c "*.py"

# Using a prompt from a file
argoagent -p prompt.txt

# Counting tokens without making an API request
argoagent "Your prompt here" -n

# Using verbose logging
argoagent "Your prompt here" -v
```

## Command-line Options

- `prompt`: The prompt to send to the model (positional argument)
- `-p, --prompt_file`: Path to a file containing the prompt
- `-c, --context`: Path(s) to file(s), directory(ies), or wildcard pattern(s) containing context
- `-s, --system`: System prompt to use (see available options below)
- `-u, --argo_url`: ARGO API endpoint URL
- `-a, --argo_user`: User for the Argo API request
- `-m, --model`: Model to use for the prompt
- `-t, --temperature`: Sampling temperature (0-2)
- `-o, --top_p`: Top-p sampling (0-1)
- `-x, --max_tokens`: Maximum number of tokens in the response
- `-n, --number_of_tokens`: Only count and display the number of tokens
- `-v, --verbose`: Enable verbose logging

## Available System Prompts

- `code_review`: For reviewing code and suggesting improvements
- `linux_help`: For getting help with Linux commands
- `linux_quick`: For quick Linux command suggestions without explanations
- `debug`: For debugging code issues
- `doc`: For generating documentation
- `token_counter`: For counting tokens in text

## Environment Variables

You can set these environment variables to avoid specifying them in every command:

```bash
export ARGO_URL="your_api_url"
export ARGO_USER="your_username"
```

## Dependencies

### Required Dependencies
- requests>=2.31.0
- rich>=13.7.0
- PyMuPDF>=1.23.8 (for PDF handling)
- python-docx>=1.0.1 (for DOCX handling)
- openpyxl>=3.1.2 (for Excel handling)
- python-pptx>=0.6.23 (for PowerPoint handling)
- markdown>=3.5.1 (for Markdown handling)

### Development Dependencies
- pytest>=7.4.3
- black>=23.11.0
- isort>=5.12.0
- mypy>=1.7.1
- pylint>=3.0.2

## Examples

### Code Review
```bash
argoagent "Review this code" -c path/to/code.py -s code_review
```

### Linux Command Help
```bash
argoagent "How do I find all files modified in the last 7 days?" -s linux_quick
```

### Document Analysis
```bash
argoagent "Summarize this document" -c document.pdf
```

### Multiple File Analysis
```bash
argoagent "Compare these files" -c "*.py"
```

### Debugging Code
```bash
argoagent "Debug this error" -c error.log -s debug
```

### Generating Documentation
```bash
argoagent "Generate documentation" -c source.py -s doc
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
