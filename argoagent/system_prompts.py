"""System prompts for different use cases."""

import logging
from pathlib import Path
from typing import Dict, List

# Configure logger
logger = logging.getLogger(__name__)

# Get the directory containing this file
CURRENT_DIR = Path(__file__).parent
PROMPT_DIR = CURRENT_DIR / "system_prompts"


def load_prompts() -> Dict[str, str]:
    """Load system prompts from files."""
    prompts = {}
    try:
        for file in PROMPT_DIR.glob("*.md"):
            prompt_name = file.stem  # Use the file name (without extension) as the key
            with file.open("r", encoding="utf-8") as f:
                prompts[prompt_name] = f.read().strip()
        logger.info(f"Loaded {len(prompts)} system prompts from {PROMPT_DIR}")
    except Exception as e:
        logger.error(f"Error loading system prompts: {str(e)}")
        # Fall back to empty prompts dictionary
        prompts = {}
    return prompts


def get_system_prompt(prompt_name: str) -> str:
    """Get a system prompt by name."""
    return SYSTEM_PROMPTS.get(prompt_name, "")


def list_available_prompts() -> List[str]:
    """Get a list of available system prompt names."""
    return sorted(SYSTEM_PROMPTS.keys())


def format_prompt_list() -> str:
    """Get a formatted list of available system prompts for display."""
    return "\n".join(f"- {name}" for name in list_available_prompts())


# Load prompts at runtime
SYSTEM_PROMPTS = load_prompts()
