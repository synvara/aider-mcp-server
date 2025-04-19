import json
import os
import subprocess
from typing import Any, Union

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from aider_mcp_server.atoms.logging import get_logger
from aider_mcp_server.atoms.tools.aider_ai_code import code_with_aider
from aider_mcp_server.atoms.tools.aider_list_models import list_models
from aider_mcp_server.atoms.utils import DEFAULT_EDITOR_MODEL

# Configure logging
logger = get_logger(__name__)

# Define MCP tools
AIDER_AI_CODE_TOOL = Tool(
    name="aider_ai_code",
    description=(
        "Run Aider to perform AI coding tasks based on the provided prompt and files"
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "ai_coding_prompt": {
                "type": "string",
                "description": "The prompt for the AI to execute",
            },
            "relative_editable_files": {
                "type": "array",
                "description": "LIST of relative paths to files that can be edited",
                "items": {"type": "string"},
            },
            "relative_readonly_files": {
                "type": "array",
                "description": (
                    "LIST of relative paths to files that can be read but not "
                    "edited, add files that are not editable but useful for context"
                ),
                "items": {"type": "string"},
            },
            "model": {
                "type": "string",
                "description": (
                    "The primary AI model Aider should use for generating code, "
                    "leave blank unless model is specified in the request"
                ),
            },
        },
        "required": ["ai_coding_prompt", "relative_editable_files"],
    },
)

LIST_MODELS_TOOL = Tool(
    name="list_models",
    description="List available models that match the provided substring",
    inputSchema={
        "type": "object",
        "properties": {
            "substring": {
                "type": "string",
                "description": "Substring to match against available models",
            }
        },
    },
)


def is_git_repository(directory: str) -> tuple[bool, Union[str, None]]:
    """
    Check if the specified directory is a git repository.

    Args:
        directory (str): The directory to check.

    Returns:
        tuple[bool, Union[str, None]]: A tuple containing a boolean indicating if
            it's a git repo, and an error message if it's not.
    """
    try:
        # Make sure the directory exists
        if not os.path.isdir(directory):
            return False, f"Directory does not exist: {directory}"

        # Use the git command with -C option to specify the working directory
        # This way we don't need to change our current directory
        result = subprocess.run(
            ["git", "-C", directory, "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0 and result.stdout.strip() == "true":
            return True, None
        else:
            return False, result.stderr.strip() or "Directory is not a git repository"

    except subprocess.SubprocessError as e:
        return False, f"Error checking git repository: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error checking git repository: {str(e)}"


def process_aider_ai_code_request(
    params: dict[str, Any],
    editor_model: str,
    current_working_dir: str,
) -> dict[str, Any]:
    """
    Process an aider_ai_code request.

    Args:
        params (Dict[str, Any]): The request parameters.
        editor_model (str): The editor model to use.
        current_working_dir (str): The current working directory where git repo
            is located.

    Returns:
        Dict[str, Any]: The response data.
    """
    ai_coding_prompt = params.get("ai_coding_prompt", "")
    relative_editable_files = params.get("relative_editable_files", [])
    relative_readonly_files = params.get("relative_readonly_files", [])

    # Ensure relative_editable_files is a list
    if isinstance(relative_editable_files, str):
        logger.info(
            f"Converting single editable file string to list: {relative_editable_files}"
        )
        relative_editable_files = [relative_editable_files]

    # Ensure relative_readonly_files is a list
    if isinstance(relative_readonly_files, str):
        logger.info(
            f"Converting single readonly file string to list: {relative_readonly_files}"
        )
        relative_readonly_files = [relative_readonly_files]

    # Get the model from request parameters if provided
    request_model = params.get("model")

    # Log the request details
    logger.info(f"AI Coding Request: Prompt: '{ai_coding_prompt}'")
    logger.info(f"Editable files: {relative_editable_files}")
    logger.info(f"Readonly files: {relative_readonly_files}")
    logger.info(f"Editor model: {editor_model}")
    if request_model:
        logger.info(f"Request-specified model: {request_model}")

    # Use the model specified in the request if provided, otherwise use the editor model
    model_to_use = request_model if request_model else editor_model

    # Use the passed-in current_working_dir parameter
    logger.info(f"Using working directory for code_with_aider: {current_working_dir}")

    result_json = code_with_aider(
        ai_coding_prompt=ai_coding_prompt,
        relative_editable_files=relative_editable_files,
        relative_readonly_files=relative_readonly_files,
        model=model_to_use,
        working_dir=current_working_dir,
    )

    # Parse the JSON string result
    try:
        result_dict = json.loads(result_json)
    except json.JSONDecodeError as e:
        logger.error(f"Error: Failed to parse JSON response from code_with_aider: {e}")
        logger.error(f"Received raw response: {result_json}")
        return {"error": "Failed to process AI coding result"}

    logger.info(
        f"AI Coding Request Completed. Success: {result_dict.get('success', False)}"
    )
    return {
        "success": result_dict.get("success", False),
        "diff": result_dict.get("diff", "Error retrieving diff"),
    }


def process_list_models_request(params: dict[str, Any]) -> dict[str, Any]:
    """
    Process a list_models request.

    Args:
        params (Dict[str, Any]): The request parameters.

    Returns:
        Dict[str, Any]: The response data.
    """
    substring = params.get("substring", "")

    # Log the request details
    logger.info(f"List Models Request: Substring: '{substring}'")

    models = list_models(substring)
    logger.info(f"Found {len(models)} models matching '{substring}'")

    return {"models": models}


def handle_request(
    request: dict[str, Any],
    current_working_dir: str,
    editor_model: str,
) -> dict[str, Any]:
    """
    Handle incoming MCP requests according to the MCP protocol.

    Args:
        request (Dict[str, Any]): The request JSON.
        current_working_dir (str): The current working directory. Must be a valid
            git repository.
        editor_model (str): The editor model to use.

    Returns:
        Dict[str, Any]: The response JSON.
    """
    try:
        # Validate current_working_dir is provided and is a git repository
        if not current_working_dir:
            error_msg = (
                "Error: current_working_dir is required. Please provide a valid "
                "git repository path."
            )
            logger.error(error_msg)
            return {"error": error_msg}

        # MCP protocol requires 'name' and 'parameters' fields
        if "name" not in request:
            logger.error("Error: Received request missing 'name' field.")
            return {"error": "Missing 'name' field in request"}

        request_type = request.get("name")
        params = request.get("parameters", {})

        logger.info(
            f"Received request: Type='{request_type}', CWD='{current_working_dir}'"
        )

        # Validate that the current_working_dir is a git repository before
        # changing to it
        is_git_repo, error_message = is_git_repository(current_working_dir)
        if not is_git_repo:
            error_msg = (
                f"Error: The specified directory '{current_working_dir}' is not "
                f"a valid git repository: {error_message}"
            )
            logger.error(error_msg)
            return {"error": error_msg}

        # Set working directory
        logger.info(f"Changing working directory to: {current_working_dir}")
        os.chdir(current_working_dir)

        # Route to the appropriate handler based on request type
        if request_type == "aider_ai_code":
            return process_aider_ai_code_request(
                params, editor_model, current_working_dir
            )

        elif request_type == "list_models":
            return process_list_models_request(params)

        else:
            # Unknown request type
            logger.warning(f"Warning: Unknown request type received: {request_type}")
            return {"error": f"Unknown request type: {request_type}"}

    except Exception as e:
        # Handle any errors
        logger.exception(
            f"Critical Error: Unhandled exception during request processing: {str(e)}"
        )
        return {"error": f"Internal server error: {str(e)}"}


async def serve(
    editor_model: str = DEFAULT_EDITOR_MODEL,
    current_working_dir: str = None,
) -> None:
    """
    Start the MCP server following the Model Context Protocol.

    The server reads JSON requests from stdin and writes JSON responses to stdout.
    Each request should contain a 'name' field indicating the tool to invoke, and
    a 'parameters' field with the tool-specific parameters.

    Args:
        editor_model (str, optional): The editor model to use.
            Defaults to DEFAULT_EDITOR_MODEL.
        current_working_dir (str, required): The current working directory.
            Must be a valid git repository.

    Raises:
        ValueError: If current_working_dir is not provided or is not a git repository.
    """
    logger.info("Starting Aider MCP Server")
    logger.info(f"Editor Model: {editor_model}")

    # Validate current_working_dir is provided
    if not current_working_dir:
        error_msg = (
            "Error: current_working_dir is required. Please provide a valid git "
            "repository path."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info(f"Initial Working Directory: {current_working_dir}")

    # Validate that the current_working_dir is a git repository
    is_git_repo, error_message = is_git_repository(current_working_dir)
    if not is_git_repo:
        error_msg = (
            f"Error: The specified directory '{current_working_dir}' is not a "
            f"valid git repository: {error_message}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.info(f"Validated git repository at: {current_working_dir}")

    # Set working directory
    logger.info(f"Setting working directory to: {current_working_dir}")
    os.chdir(current_working_dir)

    # Create the MCP server
    server = Server(tools=[AIDER_AI_CODE_TOOL, LIST_MODELS_TOOL])

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """Register all available tools with the MCP server."""
        return [AIDER_AI_CODE_TOOL, LIST_MODELS_TOOL]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls from the MCP client."""
        logger.info(f"Received Tool Call: Name='{name}'")
        # Ensure arguments is always a dictionary, even if None initially
        arguments = arguments or {}

        # Handle based on tool name
        if name == "aider_ai_code":
            try:
                response_data = process_aider_ai_code_request(
                    arguments,
                    editor_model=editor_model,
                    current_working_dir=current_working_dir,
                )
                # Ensure response_data always contains a string for the diff
                diff_content = response_data.get(
                    "diff", "No diff information provided."
                )
                # Return success/failure status as a simple string message for now
                # Ideally, MCP protocol might support structured success/error better
                status_msg = "Success" if response_data.get("success") else "Failure"
                # Combine status and diff into the TextContent
                full_content = f"{status_msg}\n\nDiff:\n```diff\n{diff_content}\n```"
                return [TextContent(text=full_content)]
            except Exception as e:
                logger.error(f"Error processing tool '{name}': {str(e)}", exc_info=True)
                return [TextContent(text=f"Error processing tool '{name}': {str(e)}")]
        elif name == "list_models":
            try:
                response_data = process_list_models_request(arguments)
                models_list = response_data.get("models", [])
                return [
                    TextContent(
                        text=f"Available models:\n{json.dumps(models_list, indent=2)}"
                    )
                ]
            except Exception as e:
                logger.error(f"Error processing tool '{name}': {str(e)}", exc_info=True)
                return [TextContent(text=f"Error processing tool '{name}': {str(e)}")]
        else:
            logger.warning(f"Received call for unknown tool: {name}")
            return [TextContent(text=f"Unknown tool: {name}")]

    # Start the server using stdio
    logger.info(
        f"Starting server with editor_model='{editor_model}' and "
        f"cwd='{current_working_dir}'"
    )
    await stdio_server(server)
