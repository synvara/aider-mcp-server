# from typing import List # Removed unnecessary import

from aider.models import fuzzy_match_models


def list_models(substring: str) -> list[str]:  # Changed List to list
    """
    List available models that match the provided substring.

    Args:
        substring (str): Substring to match against available models.

    Returns:
        list[str]: List of model names matching the substring.
            # Changed List to list in docstring - NOTE: Line break added
    """
    return fuzzy_match_models(substring)
