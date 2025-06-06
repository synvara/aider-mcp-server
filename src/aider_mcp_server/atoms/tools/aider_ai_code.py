import json
import os
import os.path
import subprocess
from typing import Union

from aider.coders import Coder
from aider.io import InputOutput
from aider.models import Model, fuzzy_match_models

from aider_mcp_server.atoms.logging import get_logger

# Configure logging for this module
logger = get_logger(__name__)

# Type alias for response dictionary
ResponseDict = dict[str, Union[bool, str]]


def _get_changes_diff_or_content(
    relative_editable_files: list[str], working_dir: str | None = None
) -> str:
    """
    Get the git diff for the specified files, or their content if git fails.

    Args:
        relative_editable_files: List of files to check for changes
        working_dir: The working directory where the git repo is located
    """
    diff = ""
    # Log current directory for debugging
    current_dir = os.getcwd()
    logger.info(f"Current directory during diff: {current_dir}")
    if working_dir:
        logger.info(f"Using working directory: {working_dir}")

    # Always attempt to use git
    files_arg = " ".join(relative_editable_files)
    logger.info(f"Attempting to get git diff for: {' '.join(relative_editable_files)}")

    try:
        # Use git -C to specify the repository directory
        if working_dir:
            diff_cmd = f"git -C {working_dir} diff -- {files_arg}"
        else:
            diff_cmd = f"git diff -- {files_arg}"

        logger.info(f"Running git command: {diff_cmd}")
        diff = subprocess.check_output(
            diff_cmd, shell=True, text=True, stderr=subprocess.PIPE
        )
        logger.info("Successfully obtained git diff.")
    except subprocess.CalledProcessError as e:
        logger.warning(
            f"Git diff command failed with exit code {e.returncode}. "
            f"Error: {e.stderr.strip()}"
        )
        logger.warning("Falling back to reading file contents.")
        diff = "Git diff failed. Current file contents:\n\n"
        for file_path in relative_editable_files:
            full_path = (
                os.path.join(working_dir, file_path) if working_dir else file_path
            )
            if os.path.exists(full_path):
                try:
                    with open(full_path) as f:
                        content = f.read()
                        diff += f"--- {file_path} ---\n{content}\n\n"
                        logger.info(f"Read content for {file_path}")
                except Exception as read_e:
                    logger.error(
                        f"Failed reading file {full_path} for content fallback: "
                        f"{read_e}"
                    )
                    diff += f"--- {file_path} --- (Error reading file)\n\n"
            else:
                logger.warning(f"File {full_path} not found during content fallback.")
                diff += f"--- {file_path} --- (File not found)\n\n"
    except Exception as e:
        logger.error(f"Unexpected error getting git diff: {str(e)}")
        # Provide error in diff string as fallback
        diff = f"Error getting git diff: {str(e)}\n\n"
    return diff


def _check_for_meaningful_changes(
    relative_editable_files: list[str], working_dir: str | None = None
) -> bool:
    """
    Check if the edited files contain meaningful content.

    Args:
        relative_editable_files: List of files to check
        working_dir: The working directory where files are located
    """
    for file_path in relative_editable_files:
        # Use the working directory if provided
        full_path = os.path.join(working_dir, file_path) if working_dir else file_path
        logger.info(f"Checking for meaningful content in: {full_path}")

        if os.path.exists(full_path):
            try:
                with open(full_path) as f:
                    content = f.read()
                    # Check if the file has more than just whitespace or a single
                    # comment line, or contains common code keywords.
                    # This is a heuristic.
                    stripped_content = content.strip()
                    if stripped_content and (
                        len(stripped_content.split("\n")) > 1
                        or any(
                            kw in content
                            for kw in [
                                "def ",
                                "class ",
                                "import ",
                                "from ",
                                "async def",
                            ]
                        )
                    ):
                        logger.info(f"Meaningful content found in: {file_path}")
                        return True
            except Exception as e:
                logger.error(
                    f"Failed reading file {full_path} during meaningful "
                    f"change check: {e}"
                )
                # If we can't read it, we can't confirm meaningful change
                # from this file
                continue
        else:
            logger.info(
                f"File not found or empty, skipping meaningful check: {full_path}"
            )

    logger.info("No meaningful changes detected in any editable files.")
    return False


def _process_coder_results(
    relative_editable_files: list[str], working_dir: str | None = None
) -> ResponseDict:
    """
    Process the results after Aider has run, checking for meaningful changes
    and retrieving the diff or content.

    Args:
        relative_editable_files: List of files that were edited
        working_dir: The working directory where the git repo is located

    Returns:
        Dictionary with success status and diff output
    """
    diff_output = _get_changes_diff_or_content(relative_editable_files, working_dir)
    logger.info("Checking for meaningful changes in edited files...")
    has_meaningful_content = _check_for_meaningful_changes(
        relative_editable_files, working_dir
    )

    if has_meaningful_content:
        logger.info("Meaningful changes found. Processing successful.")
        return {"success": True, "diff": diff_output}
    else:
        logger.warning(
            "No meaningful changes detected. Processing marked as unsuccessful."
        )
        # Even if no meaningful content, provide the diff/content if available
        return {
            "success": False,
            "diff": diff_output
            or "No meaningful changes detected and no diff/content available.",
        }


def _format_response(response: ResponseDict) -> str:
    """
    Format the response dictionary as a JSON string.

    Args:
        response: Dictionary containing success status and diff output

    Returns:
        JSON string representation of the response
    """
    return json.dumps(response, indent=4)


def code_with_aider(
    ai_coding_prompt: str,
    relative_editable_files: list[str],
    relative_readonly_files: list[str] | None = None,
    model: str = "gemini/gemini-2.5-pro-exp-03-25",
    working_dir: str | None = None,
) -> str:
    """
    Run Aider to perform AI coding tasks based on the provided prompt and files.

    Args:
        ai_coding_prompt (str): The prompt for the AI to execute.
        relative_editable_files (list[str]): List of files that can be edited.
        relative_readonly_files (list[str] | None, optional):
            List of files that can be read but not edited. Defaults to None.
        model (str, optional): The model to use.
            Defaults to "gemini/gemini-2.5-pro-exp-03-25".
        working_dir (str, required): The working directory where git repository
            is located and files are stored.

    Returns:
        str: JSON string containing success status and diff output.
    """
    # Fix for B006: Use None as default and initialize inside
    if relative_readonly_files is None:
        relative_readonly_files = []

    if working_dir is None:
        logger.error("Error: working_dir must be provided")
        return _format_response(
            {"success": False, "diff": "Error: working_dir not provided"}
        )

    # --- Start: Conditional configuration for CI (Vertex AI/ADC) vs Local (API Key) ---
    is_ci_environment = os.getenv("GITHUB_ACTIONS") == "true"
    effective_model = model

    if is_ci_environment:
        logger.info("CI environment detected. Configuring for Vertex AI with ADC.")
        # Prepend prefix for Vertex AI models
        if not model.startswith("vertex_ai/"):
            effective_model = f"vertex_ai/{model.split('/')[-1]}"  # Use base model name
            logger.info(f"Adjusted model name for Vertex AI: {effective_model}")
        else:
            logger.info("Model name already has vertex_ai/ prefix.")

        # Set environment variables for litellm/Vertex AI ADC
        vertex_project = "github-actions-457316"
        vertex_location = "us-central1"  # Or your desired region
        os.environ["VERTEX_PROJECT"] = vertex_project
        os.environ["VERTEX_LOCATION"] = vertex_location
        logger.info(f"Set VERTEX_PROJECT={vertex_project}")
        logger.info(f"Set VERTEX_LOCATION={vertex_location}")
        # Ensure API key is not interfering (though ADC should take precedence)
        if "GOOGLE_API_KEY" in os.environ:
            logger.warning(
                "GOOGLE_API_KEY found in environment, ADC should still be used"
                " for Vertex."
            )
            # Consider unsetting if issues persist: del os.environ["GOOGLE_API_KEY"]
    else:
        logger.info(
            "Local environment detected. Assuming API key "
            "(e.g., GEMINI_API_KEY) is available."
        )
        # Use the model name directly, litellm should handle API key auth
        logger.info(f"Using model name for API key auth: {effective_model}")
    # --- End: Conditional configuration ---

    # Log inputs
    logger.info("Received Aider AI Code request:")
    logger.info(f"  Prompt: {ai_coding_prompt}")
    logger.info(f"  Editable Files: {relative_editable_files}")
    logger.info(f"  Readonly Files: {relative_readonly_files}")
    logger.info(
        f"  Model: {effective_model}"
    )  # Log the potentially adjusted model name
    logger.info(f"  Working Dir: {working_dir}")

    # Check if the working directory is valid
    if not os.path.isdir(working_dir):
        error_msg = (
            f"Error: working_dir '{working_dir}' does not exist or is not a directory."
        )
        logger.error(error_msg)
        return _format_response({"success": False, "diff": error_msg})

    # --- Start: Add Model Validation ---
    logger.info(f"Validating model: {effective_model}")

    # Allow the specific experimental model suggested by the API error message,
    # even if fuzzy_match_models doesn't list it.
    allowed_experimental = [
        "gemini/gemini-2.5-pro-exp-03-25",
        "vertex_ai/gemini-2.5-pro-exp-03-25",
    ]
    if effective_model in allowed_experimental:
        logger.warning(
            f"Allowing potentially unlisted experimental model: {effective_model}"
        )
        is_model_valid = True
    else:
        valid_models = fuzzy_match_models(
            effective_model
        )  # Validate adjusted model name
        # Check if the *exact* model name provided is in the list
        # of valid fuzzy matches.
        is_model_valid = effective_model in valid_models  # Check adjusted model name

    if not is_model_valid:
        error_msg = f"Error: Model '{effective_model}' is not recognized or available."
        logger.error(error_msg)
        # Also list possible matches if the fuzzy search found any
        if valid_models:
            possible_matches = valid_models  # Already a list of strings
            error_msg += f" Possible matches: {possible_matches}"
            logger.info(f"Possible model matches found: {possible_matches}")
        else:
            logger.info("No similar models found.")
        return _format_response({"success": False, "diff": error_msg})
    else:
        logger.info(
            f"Model '{effective_model}' validated successfully (or explicitly allowed)."
        )
    # --- End: Add Model Validation ---

    # Check if the working directory is a git repository
    # Aider usually requires this
    is_git_repo = os.path.isdir(os.path.join(working_dir, ".git"))
    if not is_git_repo:
        # We can make this check optional if needed, but it's good practice
        logger.warning(
            f"Warning: working_dir '{working_dir}' is not a git repository. "
            f"Aider might behave unexpectedly."
        )
        # Decide if we should proceed or return an error
        # - let's proceed with warning for now
        # return _format_response({
        #     "success": False,
        #     "diff": f"Error: working_dir '{working_dir}' is not a git repository."
        # })

    # Adjust file paths to be relative to the current process working directory
    # if aider is run from a different CWD than the server
    abs_editable_files = [os.path.join(working_dir, f) for f in relative_editable_files]
    abs_readonly_files = [os.path.join(working_dir, f) for f in relative_readonly_files]

    logger.info(f"Absolute Editable Files: {abs_editable_files}")
    logger.info(f"Absolute Readonly Files: {abs_readonly_files}")

    try:
        # Change to the target working directory before initializing Aider
        original_cwd = os.getcwd()
        os.chdir(working_dir)
        logger.info(f"Changed directory to: {working_dir}")

        # Create coder
        main_model = Model(effective_model)  # Use the potentially adjusted model name
        io = InputOutput(yes=True)  # Use yes=True to auto-accept changes

        # Aider's Coder.create expects paths relative to its CWD,
        # which is now working_dir
        coder = Coder.create(
            main_model=main_model,
            io=io,
            fnames=relative_editable_files,  # Pass relative paths here
            read_only_fnames=relative_readonly_files,  # Pass relative paths here
            auto_commits=False,  # Don't commit changes
            use_git=True,  # Allow Aider to use git diff if available
            show_diffs=False,
        )

        logger.info(f"Running Aider with prompt: {ai_coding_prompt}")
        coder.run(with_message=ai_coding_prompt)
        logger.info("Aider run completed.")

        # Process results after Aider run
        response = _process_coder_results(
            relative_editable_files, working_dir=None
        )  # Check diff relative to CWD

    except Exception as e:
        logger.error(f"Error during Aider execution: {str(e)}", exc_info=True)
        response = {"success": False, "diff": f"Error during Aider execution: {str(e)}"}
    finally:
        # Ensure we change back to the original directory
        os.chdir(original_cwd)
        logger.info(f"Changed directory back to: {original_cwd}")

    formatted_response = _format_response(response)
    logger.info(f"Aider AI Code Response: {formatted_response}")
    return formatted_response
