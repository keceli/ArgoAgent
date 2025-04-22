"""Task management for ArgoAgent."""

import logging
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure logger
logger = logging.getLogger(__name__)

# Get the directory containing this file
CURRENT_DIR = Path(__file__).parent
TASKS_DIR = CURRENT_DIR / "tasks"


class Task:
    """Represents a task with its configuration."""

    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        user_prompt: str,
    ):
        """Initialize a task with its configuration."""
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt

    @classmethod
    def from_dict(cls, data: Dict, default_name: str = "") -> "Task":
        """Create a Task instance from a dictionary.

        Args:
            data: Dictionary containing task configuration
            default_name: Default name to use if not specified in data
        """
        return cls(
            name=data.get("name", default_name),
            description=data.get("description", f"Task loaded from {default_name}"),
            system_prompt=data.get("system_prompt", ""),
            user_prompt=data.get("user_prompt", ""),
        )


def load_tasks() -> Dict[str, Task]:
    """Load tasks from YAML files."""
    tasks = {}
    try:
        for file in TASKS_DIR.glob("*.yaml"):
            task_name = file.stem  # Use the file name (without extension) as the key
            with file.open("r", encoding="utf-8") as f:
                task_data = yaml.safe_load(f)
                if task_data is None:  # Handle empty YAML files
                    task_data = {}
                # Pass the file name as default_name
                task = Task.from_dict(task_data, default_name=task_name)
                # Use the task's name if it was specified in YAML, otherwise use file name
                tasks[task.name or task_name] = task
            logger.debug(f"Loaded task '{task.name or task_name}' from {file}")
        logger.info(f"Loaded {len(tasks)} tasks from {TASKS_DIR}")
    except Exception as e:
        logger.error(f"Error loading tasks: {str(e)}")
        # Fall back to empty tasks dictionary
        tasks = {}
    return tasks


def get_task(task_name: str) -> Optional[Task]:
    """Get a task by name."""
    return TASKS.get(task_name)


def list_available_tasks() -> List[str]:
    """Get a list of available task names."""
    return sorted(TASKS.keys())


def format_task_list() -> str:
    """Get a formatted list of available tasks for display."""
    return "\n".join(
        f"- {name}: {TASKS[name].description}" for name in list_available_tasks()
    )


# Load tasks at runtime
TASKS = load_tasks()
