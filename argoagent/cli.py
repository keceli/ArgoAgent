"""Command-line interface for ArgoAgent."""

import argparse
import glob
import json
import logging
import os
import sys
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

from .api import ask_llm, count_tokens
from .file_handlers import get_supported_extensions, read_file_content
from .models import get_model_help_text
from .system_prompts import (
    get_system_prompt,
    list_available_prompts,
    format_prompt_list,
)

# Configure logger
logger = logging.getLogger(__name__)

# Initialize Rich console
console = Console()


class TokenLimitExceededError(Exception):
    """Raised when the total token count exceeds the specified limit."""

    pass


def handle_wildcard_pattern(
    path: str, max_tokens: Optional[int] = None
) -> Tuple[Dict[str, str], int]:
    """Handle wildcard pattern matching for files."""
    context_data: Dict[str, str] = {}
    total_tokens = 0

    matching_files = glob.glob(path)
    if not matching_files:
        logger.warning(f"No files match pattern '{path}'")
        return context_data, total_tokens

    for file_path in matching_files:
        if os.path.isfile(file_path):
            content = read_file_content(file_path)
            if content is not None:
                context_data[file_path] = content

                if max_tokens is not None:
                    file_tokens = count_tokens(content)
                    if file_tokens is not None:
                        total_tokens += file_tokens
                        if total_tokens > max_tokens:
                            raise TokenLimitExceededError(
                                f"Total tokens ({total_tokens}) exceed max_tokens ({max_tokens})"
                            )

    return context_data, total_tokens


def handle_directory(
    path: str, max_tokens: Optional[int] = None
) -> Tuple[Dict[str, str], int]:
    """Handle directory traversal for files."""
    context_data: Dict[str, str] = {}
    total_tokens = 0

    supported_extensions = get_supported_extensions()

    for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            # Only process files with supported extensions
            if any(file.lower().endswith(ext) for ext in supported_extensions):
                content = read_file_content(file_path)
                if content is not None:
                    context_data[file_path] = content

                    if max_tokens is not None:
                        file_tokens = count_tokens(content)
                        if file_tokens is not None:
                            total_tokens += file_tokens
                            if total_tokens > max_tokens:
                                raise TokenLimitExceededError(
                                    f"Total tokens ({total_tokens}) exceed max_tokens ({max_tokens})"
                                )

    return context_data, total_tokens


def handle_single_file(
    path: str, max_tokens: Optional[int] = None
) -> Tuple[Dict[str, str], int]:
    """Handle a single file."""
    context_data: Dict[str, str] = {}
    total_tokens = 0

    content = read_file_content(path)
    if content is not None:
        context_data[path] = content

        if max_tokens is not None:
            file_tokens = count_tokens(content)
            if file_tokens is not None:
                total_tokens += file_tokens
                if total_tokens > max_tokens:
                    raise TokenLimitExceededError(
                        f"Total tokens ({total_tokens}) exceed max_tokens ({max_tokens})"
                    )

    return context_data, total_tokens


def get_context_from_paths(
    paths: List[str], max_tokens: Optional[int] = None
) -> Tuple[str, int]:
    """Get context from file paths, directories, or wildcard patterns."""
    context_data: Dict[str, str] = {}
    total_tokens = 0

    for path in paths:
        try:
            # Handle wildcard patterns
            if "*" in path or "?" in path:
                new_context, new_tokens = handle_wildcard_pattern(path, max_tokens)

            # Handle directories
            elif os.path.isdir(path):
                new_context, new_tokens = handle_directory(path, max_tokens)

            # Handle single files
            elif os.path.isfile(path):
                new_context, new_tokens = handle_single_file(path, max_tokens)

            else:
                logger.warning(f"Path '{path}' does not exist")
                continue

            context_data.update(new_context)
            total_tokens += new_tokens

        except TokenLimitExceededError as e:
            logger.error(str(e))
            sys.exit(1)

    # Convert to JSON format
    return json.dumps(context_data, indent=2), total_tokens


def format_prompt_with_context(
    prompt: str, context: Optional[str], system_prompt: Optional[str] = None
) -> str:
    """Format the prompt with the given context and system prompt."""
    formatted_prompt = prompt

    if system_prompt:
        formatted_prompt = f"{system_prompt}\n\n{formatted_prompt}"

    if context is not None:
        if "{context}" in formatted_prompt:
            formatted_prompt = formatted_prompt.replace("{context}", context)
        else:
            formatted_prompt = (
                f"{formatted_prompt}\nreply based on the content here:{context}"
            )

    return formatted_prompt


def print_response(
    response: str,
    model: str,
    prompt: str,
    token_count: Optional[int] = None,
    system_prompt_name: Optional[str] = None,
) -> None:
    """Print the response with model and prompt information."""
    # Create a header with model and prompt information
    header = Text()
    header.append("Model: ", style="bold blue")
    header.append(model, style="bold green")

    if system_prompt_name:
        header.append("\nSystem Prompt: ", style="bold blue")
        header.append(system_prompt_name, style="bold magenta")

    if token_count is not None:
        header.append("\nTokens: ", style="bold blue")
        header.append(str(token_count), style="bold cyan")

    header.append("\nPrompt: ", style="bold blue")
    header.append(
        prompt[:100] + "..." if len(prompt) > 100 else prompt, style="bold yellow"
    )

    # Print the header in a panel
    console.print(Panel(header, title="ArgoAgent", border_style="blue"))

    # Print the response as markdown
    console.print(Markdown(response))


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Send a prompt to the Argo API.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Create mutually exclusive group for prompt input
    prompt_group = parser.add_mutually_exclusive_group(required=True)
    prompt_group.add_argument(
        "prompt",
        nargs="?",  # Make positional argument optional
        help="The prompt to send to the model.",
    )
    prompt_group.add_argument(
        "-p",
        "--prompt_file",
        help="Path to a file containing the prompt to send to the model.",
    )

    parser.add_argument(
        "-c",
        "--context",
        nargs="+",
        help="Path(s) to file(s), directory(ies), or wildcard pattern(s) containing context to be included in the prompt.",
    )
    parser.add_argument(
        "-s",
        "--system",
        choices=list_available_prompts(),
        help="System prompt to use. Available options:\n" + format_prompt_list(),
    )
    parser.add_argument(
        "-u",
        "--argo_url",
        default=os.getenv("ARGO_URL"),
        help="ARGO API endpoint URL.",
    )
    parser.add_argument(
        "-a",
        "--argo_user",
        default=os.getenv("ARGO_USER"),
        help="User for the Argo API request.",
    )
    parser.add_argument(
        "-m",
        "--model",
        default="gpt4olatest",
        help="Model to use for the prompt." + get_model_help_text(),
    )
    parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature (0-2). Higher values mean more creative output. Not supported by some models.",
    )
    parser.add_argument(
        "-o",
        "--top_p",
        type=float,
        default=0.9,
        help="Top-p sampling (0-1). Alternative to temperature. Not supported by some models.",
    )
    parser.add_argument(
        "-x",
        "--max_tokens",
        type=int,
        default=100000,
        help="Maximum number of tokens in the response. Will be automatically capped based on model limits.",
    )
    parser.add_argument(
        "-n",
        "--number_of_tokens",
        action="store_true",
        help="Only count and display the number of tokens in the prompt without making an API request.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )

    args = parser.parse_args()

    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    # Handle prompt file if provided
    if args.prompt_file:
        prompt_text = read_file_content(args.prompt_file)
        if prompt_text is None:
            return
    else:
        prompt_text = args.prompt

    # Get system prompt if specified
    system_prompt = None
    if args.system:
        system_prompt = get_system_prompt(args.system)
        if not system_prompt:
            logger.error(f"Invalid system prompt: {args.system}")
            return

    # Handle context if provided
    context = None
    context_tokens = 0
    if args.context:
        try:
            context, context_tokens = get_context_from_paths(
                args.context, args.max_tokens
            )
            if context_tokens > 0:
                logger.info(f"Context contains {context_tokens} tokens")
        except TokenLimitExceededError as e:
            logger.error(str(e))
            return

    # Format the prompt with context and system prompt
    formatted_prompt = format_prompt_with_context(prompt_text, context, system_prompt)

    # Count tokens in the formatted prompt
    token_count = count_tokens(formatted_prompt)
    if token_count is not None:
        logger.info(f"Prompt contains {token_count} tokens")

    # If only token count is requested, exit here
    if args.number_of_tokens:
        return

    # Make the API request with a progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Waiting for response..."),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task("", total=None)
        response = ask_llm(
            prompt=formatted_prompt,
            model=args.model,
            argo_url=args.argo_url,
            argo_user=args.argo_user,
            temperature=args.temperature,
            top_p=args.top_p,
            max_tokens=args.max_tokens,
        )

    # Print the response with model and prompt information
    print_response(response, args.model, prompt_text, token_count, args.system)


if __name__ == "__main__":
    main()
