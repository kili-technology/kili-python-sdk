"""Helpers for the asset_import."""

import warnings

SEPARATOR = "___"


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
            raise ValueError(f"Chat item missing keys : {missing_keys}")
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
        if item["id"] is not None:
            item_ids.append(item["id"])
        else:
            warnings.warn(f"No id value for chat item {item}.")

        if item["content"] is None:
            raise ValueError("Chat item content cannot be null.")

        # Check if the prompt comes from a user or a model
        if item["role"] in ["user", "system"]:
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
            if item["role"] is None:
                raise ValueError("Chat item role cannot be null.")

            # Add completion to the current prompt
            completions.append(
                {
                    "content": item["content"],
                    "title": item["role"],
                }
            )
            # Add model if not None
            if item["model"] is not None:
                models.append(item["model"])

    if current_prompt is None:
        raise ValueError(
            "No user prompt found in payload ('model' key set to None) : need at least one."
        )

    # Add the last prompt if it exists
    if current_prompt is not None:
        transformed_data["prompts"].append(
            {
                "completions": completions,
                "prompt": current_prompt["content"],
            }
        )

    chat_item_ids = SEPARATOR.join(item_ids)

    # Prepare additional_json_metadata
    additional_json_metadata = {
        "chat_id": chat_id,
        "models": SEPARATOR.join(models[-len(completions) :]),  # Join the evaluated models
        "chat_item_ids": chat_item_ids,  # Concatenate all item IDs
        "text": f"Chat_id: {chat_id}\n\nChat_item_ids: {chat_item_ids}",
    }

    return transformed_data, additional_json_metadata
