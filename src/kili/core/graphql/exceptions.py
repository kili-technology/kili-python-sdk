"""Helper functions to extract context from GraphQL error messages."""
import ast
from typing import Dict, Optional


def extract_error_context(message: str) -> Optional[Dict[str, str]]:
    """Parse the string error message to extract the first context information."""
    try:
        parsed_errors = ast.literal_eval(message)
        return parsed_errors[0].get("extensions").get("context")
    except (SyntaxError, ValueError):
        return None
