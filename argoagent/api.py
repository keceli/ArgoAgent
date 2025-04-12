"""Core API functionality for ArgoAgent."""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import tiktoken

from .models import validate_model

# Configure logger
logger = logging.getLogger(__name__)

# Constants
DEFAULT_SYSTEM_PROMPT = "You are a helpful AI assistant."
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9
DEFAULT_MAX_TOKENS = 4096


def make_api_request(
    url: str, payload: str, headers: Dict[str, str]
) -> Tuple[str, float]:
    """Make an API request to the specified URL with retry logic."""
    start_time = time.time()

    # Configure retry strategy
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504],
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))

    try:
        response = session.post(url, data=payload, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making POST request: {str(e)}")
        logger.debug(f"Arguments: url={url}, payload={payload}, headers={headers}")
        raise

    end_time = time.time()
    response_time = end_time - start_time

    try:
        response_json = response.json().get("response", "")
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing response: {str(e)}")
        logger.debug(f"Response content: {response.text}")
        raise

    return response_json, response_time


def save_interaction_to_json(data: Dict, response: str, response_time: float) -> None:
    """Save interaction details to a timestamped JSON file."""
    # Create interactions directory if it doesn't exist
    interactions_dir = Path("interactions")
    interactions_dir.mkdir(exist_ok=True)

    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = interactions_dir / f"{data['user']}_{data['model']}_{timestamp}.json"

    # Prepare interaction data
    interaction_data = {
        "timestamp": datetime.now().isoformat(),
        "request": {
            "prompt": data["prompt"][0],
            "model": data["model"],
            "parameters": {
                "temperature": data.get("temperature"),
                "top_p": data.get("top_p"),
                "max_tokens": data.get("max_tokens"),
                "max_completion_tokens": data.get("max_completion_tokens"),
            },
            "system": data["system"],
        },
        "response": {
            "content": response,
            "time_taken": response_time,
        },
    }

    # Save to file
    try:
        with open(filename, "w") as f:
            json.dump(interaction_data, f, indent=2)
        logger.info(f"Interaction saved to: {filename}")
    except OSError as e:
        logger.error(f"Error saving interaction: {str(e)}")


def validate_parameters(temperature: float, top_p: float, max_tokens: int) -> None:
    """Validate parameter values."""
    if not 0 <= temperature <= 2:
        raise ValueError(f"Temperature must be between 0 and 2, got {temperature}")

    if not 0 <= top_p <= 1:
        raise ValueError(f"Top-p must be between 0 and 1, got {top_p}")

    if max_tokens <= 0:
        raise ValueError(f"Max tokens must be positive, got {max_tokens}")


def ask_llm(
    prompt: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    model: str = "gpt4olatest",
    record: bool = True,
    **kwargs,
) -> str:
    """Ask the LLM a prompt and return the response."""
    # Use environment variables or kwargs for URL and user
    argo_url = kwargs.get("argo_url", os.getenv("ARGO_URL"))
    argo_user = kwargs.get("argo_user", os.getenv("ARGO_USER"))

    if not argo_url or not argo_user:
        raise ValueError(
            "ARGO_URL and ARGO_USER must be set either as environment variables or in kwargs"
        )

    # Validate model and get configuration
    try:
        model_config = validate_model(model)
    except ValueError as e:
        logger.error(str(e))
        return ""

    # Get parameters with defaults
    temperature = kwargs.get("temperature", DEFAULT_TEMPERATURE)
    top_p = kwargs.get("top_p", DEFAULT_TOP_P)
    max_tokens = kwargs.get("max_tokens", DEFAULT_MAX_TOKENS)

    # Validate parameters
    try:
        validate_parameters(temperature, top_p, max_tokens)
    except ValueError as e:
        logger.error(str(e))
        return ""

    # Prepare the API request data
    data = {
        "user": argo_user,
        "model": model,
        "system": system_prompt,
        "prompt": [prompt],
        "stop": [],
    }

    # Add parameters based on model support
    if model_config["supports_standard_params"]:
        data.update(
            {
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": min(max_tokens, model_config["max_tokens"]),
            }
        )
    else:
        # For models like gpto1preview, gpto1mini, gpto3mini
        data["max_completion_tokens"] = min(max_tokens, model_config["max_tokens"])

    # Convert data to JSON payload
    payload = json.dumps(data)
    headers = {"Content-Type": "application/json"}

    # Make API request
    response, response_time = make_api_request(
        url=argo_url, payload=payload, headers=headers
    )

    logger.info(f"Response received in {response_time:.2f} seconds")

    # Save interaction if recording is enabled
    if record:
        save_interaction_to_json(data, response, response_time)

    return response


def count_tokens(text: str, model: str = "gpt-4") -> Optional[int]:
    """Count the number of tokens in a text string."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception as e:
        logger.error(f"Error counting tokens: {str(e)}")
        return None
