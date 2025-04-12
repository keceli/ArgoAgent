"""
ArgoAgent - A Python package for interacting with Argo API.

Provides core functionalities for API requests, model validation, token counting, and CLI interaction.
"""

from .api import ask_llm, count_tokens
from .models import VALID_MODELS, validate_model
import logging

__version__ = "0.1.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

__all__ = ["ask_llm", "count_tokens", "VALID_MODELS", "validate_model"]
