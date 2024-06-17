"""Helpers for the asset_import."""

import warnings


def is_chat_format(data, required_keys):
    """Checks if llm file data is in chat format."""
    if isinstance(data, dict):
        return False

    if not isinstance(data, list):
        warnings.warn("Json file is not an array.")
        return False

    # Check each item in the array
    for item in data:
        # Ensure each item is a dictionary with the required keys
        if not isinstance(item, dict) or not required_keys.issubset(item.keys()):
            missing_keys = required_keys - set(item.keys())
            warnings.warn(f"Array item missing keys : {missing_keys}", stacklevel=3)
            return False
    return True


def process_json(data):
    """Processes the llm file data : converts it to Kili format is chat format is present."""
    # Initialize the transformed structure
    transformed_data = {"prompts": [], "type": "markdown", "version": "0.1"}

    # Temporary variables for processing
    current_prompt = None
    completions = []
    models = []  # To store models for determining the last two
    item_ids = []  # To store all item IDs for concatenation
    chat_id = None

    for item in data:
        chat_id = item.get("chat_id", None)
        item_ids.append(item["id"])

        # Check if the model is null (indicating a prompt)
        if item["model"] is None:
            # If there's an existing prompt being processed, add it to the prompts list
            if current_prompt is not None:
                transformed_data["prompts"].append(
                    {
                        "completions": completions,
                        "prompt": current_prompt["content"],
                    }
                )
                completions = []  # Reset completions for the next prompt

            # Update the current prompt
            current_prompt = item
        else:
            # Add completion to the current prompt
            completions.append(
                {
                    "content": item["content"],
                    "title": item["role"],
                }
            )
            # Collect model for this item
            models.append(item["model"])

    # Add the last prompt if it exists
    if current_prompt is not None:
        transformed_data["prompts"].append(
            {
                "completions": completions,
                "prompt": current_prompt["content"],
            }
        )

    # Prepare additional_json_metadata
    additional_json_metadata = {
        "chat_id": chat_id,
        "models": "_".join(models[-2:]),  # Join the last two models
        "chat_item_ids": "_".join(item_ids),  # Concatenate all item IDs
    }

    return transformed_data, additional_json_metadata
