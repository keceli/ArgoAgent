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
        goal: str,
        system_prompt: str,
        user_prompt: str,
    ):
        """Initialize a task with its configuration."""
        self.name = name
        self.description = description
        self.goal = goal
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt

    @classmethod
    def from_dict(cls, data: Dict) -> "Task":
        """Create a Task instance from a dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            goal=data.get("goal", ""),
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
                tasks[task_name] = Task.from_dict(task_data)
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
