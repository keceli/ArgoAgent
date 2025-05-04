"""Model configurations and validation for ArgoAgent."""

VALID_MODELS = {
    "gpt35": {"max_tokens": 4096, "supports_standard_params": True},
    "gpt35large": {"max_tokens": 16384, "supports_standard_params": True},
    "gpt4": {"max_tokens": 8192, "supports_standard_params": True},
    "gpt4large": {"max_tokens": 32768, "supports_standard_params": True},
    "gpt4turbo": {"max_tokens": 4096, "supports_standard_params": True},
    "gpt4o": {"max_tokens": 16384, "supports_standard_params": True},
    "gpt4olatest": {"max_tokens": 16384, "supports_standard_params": True},
    "gpto1preview": {"max_tokens": 16384, "supports_standard_params": False},
    "gpto1mini": {"max_tokens": 65536, "supports_standard_params": False},
    "gpto3mini": {"max_tokens": 100000, "supports_standard_params": False},
    "gpto1": {"max_tokens": 200000, "supports_standard_params": False},
}


def validate_model(model_name):
    """Validate the model name and return model configuration."""
    if model_name not in VALID_MODELS:
        valid_models = "\n- ".join([""] + list(VALID_MODELS.keys()))
        raise ValueError(
            f"Invalid model name: {model_name}. Valid models are:{valid_models}"
        )
    return VALID_MODELS[model_name]


def get_model_help_text():
    """Generate help text for model information."""
    help_text = "\n\nAvailable models and their specifications:\n"

    for model, config in VALID_MODELS.items():
        help_text += f"\n\n{model}"
        help_text += f"\n{'=' * len(model)}"  # Add underlining for model name
        help_text += f"\n  • Max tokens: {config['max_tokens']}"
        help_text += f"\n  • Supports standard parameters (temperature, top_p): {config['supports_standard_params']}"

        # Add special notes for specific models
        if model == "gpt4turbo":
            help_text += "\n  • Note: This model responds much slower than GPT-3.5"
        elif model == "gpto1preview":
            help_text += "\n  • Note: Will be retired on April 1, 2025"
            help_text += (
                "\n  • Only uses 'user prompt' and 'max_completion_tokens' fields"
            )
        elif model in ["gpto1mini", "gpto3mini"]:
            help_text += "\n  • Note: Only available in dev environment"

    # Add two newlines at the end to separate from other help text
    help_text += "\n\n"
    return help_text
