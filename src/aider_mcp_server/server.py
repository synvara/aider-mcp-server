import json
import sys
import os
import asyncio
import logging
from typing import Dict, Any, Optional, List

import mcp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from aider_mcp_server.atoms.logging import get_logger
from aider_mcp_server.atoms.utils import DEFAULT_EDITOR_MODEL
from aider_mcp_server.atoms.tools.aider_ai_code import code_with_aider
from aider_mcp_server.atoms.tools.aider_list_models import list_models

# Configure logging
logger = get_logger(__name__)

def process_aider_ai_code_request(params: Dict[str, Any], editor_model: str, architect_model: Optional[str]) -> Dict[str, Any]:
    """
    Process an aider_ai_code request.
    
    Args:
        params (Dict[str, Any]): The request parameters.
        editor_model (str): The editor model to use.
        architect_model (Optional[str]): The architect model to use if architect mode is enabled.
        
    Returns:
        Dict[str, Any]: The response data.
    """
    ai_coding_prompt = params.get("ai_coding_prompt", "")
    relative_editable_files = params.get("relative_editable_files", [])
    relative_readonly_files = params.get("relative_readonly_files", [])
    # Get the model from request parameters if provided
    request_model = params.get("model")
    
    use_architect = bool(architect_model)
    
    # Log the request details
    logger.info(f"AI Coding Request: Prompt: '{ai_coding_prompt}'")
    logger.info(f"Editable files: {relative_editable_files}")
    logger.info(f"Readonly files: {relative_readonly_files}")
    logger.info(f"Using architect mode: {use_architect}")
    logger.info(f"Editor model: {editor_model}")
    if use_architect:
        logger.info(f"Architect model: {architect_model}")
    if request_model:
        logger.info(f"Request-specified model: {request_model}")

    # Use the model specified in the request if provided, otherwise use the default logic
    model_to_use = request_model if request_model else (architect_model if use_architect else editor_model)
    
    result_json = code_with_aider(
        ai_coding_prompt=ai_coding_prompt,
        relative_editable_files=relative_editable_files,
        relative_readonly_files=relative_readonly_files,
        model=model_to_use,
        editor_model=editor_model if use_architect else None,
        use_architect=use_architect,
        use_git=True
    )

    # Parse the JSON string result
    try:
        result_dict = json.loads(result_json)
    except json.JSONDecodeError as e:
        logger.error(f"Error: Failed to parse JSON response from code_with_aider: {e}")
        logger.error(f"Received raw response: {result_json}")
        return {"error": "Failed to process AI coding result"}

    logger.info(f"AI Coding Request Completed. Success: {result_dict.get('success', False)}")
    return {
        "success": result_dict.get("success", False),
        "diff": result_dict.get("diff", "Error retrieving diff")
    }

def process_list_models_request(params: Dict[str, Any]) -> Dict[str, Any]:
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

def handle_request(request: Dict[str, Any], current_working_dir: str, editor_model: str, architect_model: Optional[str]) -> Dict[str, Any]:
    """
    Handle incoming MCP requests according to the MCP protocol.
    
    Args:
        request (Dict[str, Any]): The request JSON.
        current_working_dir (str): The current working directory.
        editor_model (str): The editor model to use.
        architect_model (Optional[str]): The architect model to use.
    
    Returns:
        Dict[str, Any]: The response JSON.
    """
    try:
        # MCP protocol requires 'name' and 'parameters' fields
        if "name" not in request:
            logger.error("Error: Received request missing 'name' field.")
            return {"error": "Missing 'name' field in request"}
        
        request_type = request.get("name")
        params = request.get("parameters", {})
        
        logger.info(f"Received request: Type='{request_type}', CWD='{current_working_dir}'")
        
        # Set working directory if specified
        if current_working_dir and current_working_dir != ".":
            logger.info(f"Changing working directory to: {current_working_dir}")
            os.chdir(current_working_dir)
        
        # Route to the appropriate handler based on request type
        if request_type == "aider_ai_code":
            return process_aider_ai_code_request(params, editor_model, architect_model)
            
        elif request_type == "list_models":
            return process_list_models_request(params)
            
        else:
            # Unknown request type
            logger.warning(f"Warning: Unknown request type received: {request_type}")
            return {"error": f"Unknown request type: {request_type}"}
            
    except Exception as e:
        # Handle any errors
        logger.exception(f"Critical Error: Unhandled exception during request processing: {str(e)}")
        return {"error": f"Internal server error: {str(e)}"}

# Define MCP tools
AIDER_AI_CODE_TOOL = Tool(
    name="aider_ai_code",
    description="Run Aider to perform AI coding tasks based on the provided prompt and files",
    inputSchema={
        "type": "object",
        "properties": {
            "ai_coding_prompt": {
                "type": "string",
                "description": "The prompt for the AI to execute"
            },
            "relative_editable_files": {
                "type": "array",
                "description": "List of files that can be edited",
                "items": {"type": "string"}
            },
            "relative_readonly_files": {
                "type": "array",
                "description": "List of files that can be read but not edited",
                "items": {"type": "string"}
            },
            "model": {
                "type": "string",
                "description": "The primary AI model Aider should use for generating code"
            }
        },
        "required": ["ai_coding_prompt", "relative_editable_files"]
    }
)

LIST_MODELS_TOOL = Tool(
    name="list_models",
    description="List available models that match the provided substring",
    inputSchema={
        "type": "object",
        "properties": {
            "substring": {
                "type": "string",
                "description": "Substring to match against available models"
            }
        }
    }
)

async def serve(editor_model: str = DEFAULT_EDITOR_MODEL, current_working_dir: str = ".", architect_model: Optional[str] = None) -> None:
    """
    Start the MCP server following the Model Context Protocol.
    
    The server reads JSON requests from stdin and writes JSON responses to stdout.
    Each request should contain a 'name' field indicating the tool to invoke, and
    a 'parameters' field with the tool-specific parameters.
    
    Args:
        editor_model (str, optional): The editor model to use. Defaults to DEFAULT_EDITOR_MODEL.
        current_working_dir (str, optional): The current working directory. Defaults to ".".
        architect_model (Optional[str], optional): The architect model to use. Defaults to None.
    """
    logger.info(f"Starting Aider MCP Server")
    logger.info(f"Editor Model: {editor_model}")
    logger.info(f"Initial Working Directory: {current_working_dir}")
    
    if architect_model:
        logger.info(f"Architect Model: {architect_model}")
        logger.info("Architect mode enabled")
    else:
        logger.info("Architect mode disabled")
    
    # Set working directory if specified
    if current_working_dir and current_working_dir != ".":
        logger.info(f"Setting working directory to: {current_working_dir}")
        os.chdir(current_working_dir)
    
    # Create the MCP server
    server = Server("aider-mcp-server")
    
    @server.list_tools()
    async def list_tools() -> List[Tool]:
        """Register all available tools with the MCP server."""
        return [
            AIDER_AI_CODE_TOOL,
            LIST_MODELS_TOOL
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle tool calls from the MCP client."""
        logger.info(f"Received Tool Call: Name='{name}'")
        logger.info(f"Arguments: {arguments}")
        
        try:
            if name == "aider_ai_code":
                logger.info(f"Processing 'aider_ai_code' tool call...")
                result = process_aider_ai_code_request(arguments, editor_model, architect_model)
                return [TextContent(
                    type="text",
                    text=json.dumps(result)
                )]
                
            elif name == "list_models":
                logger.info(f"Processing 'list_models' tool call...")
                result = process_list_models_request(arguments)
                return [TextContent(
                    type="text",
                    text=json.dumps(result)
                )]
                
            else:
                logger.warning(f"Warning: Received call for unknown tool: {name}")
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": f"Unknown tool: {name}"})
                )]
                
        except Exception as e:
            logger.exception(f"Error: Exception during tool call '{name}': {e}")
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Error processing tool {name}: {str(e)}"})
            )]
    
    # Initialize and run the server
    try:
        options = server.create_initialization_options()
        logger.info("Initializing stdio server connection...")
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server running. Waiting for requests...")
            await server.run(read_stream, write_stream, options, raise_exceptions=True)
    except Exception as e:
        logger.exception(f"Critical Error: Server stopped due to unhandled exception: {e}")
        raise
    finally:
        logger.info("Aider MCP Server shutting down.")
