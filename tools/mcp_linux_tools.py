"""Linux MCP Server integration for BeeAI agent.

This module provides utilities to create Linux system diagnostic tools using the
Model Context Protocol (MCP) linux-mcp-server. The server provides read-only
access to system information, services, processes, logs, network, and storage.
"""
import os
from pathlib import Path
from typing import List

from beeai_framework.tools.mcp import MCPTool
from mcp.client.stdio import StdioServerParameters, stdio_client


async def create_linux_tools(
    server_path: str | None = None,
    allowed_log_paths: str | None = None
) -> List[MCPTool]:
    """Create MCP Linux diagnostic tools from the linux-mcp-server.
    
    This function initializes the Linux MCP server which provides read-only
    diagnostic tools for system administration and troubleshooting.
    
    Args:
        server_path: Path to the linux-mcp-server directory.
                    If None, defaults to ~/development/linux-mcp-server
        allowed_log_paths: Comma-separated list of allowed log file paths.
                          Example: "/var/log/messages,/var/log/secure"
                          If None, uses server's default configuration.
    
    Returns:
        List[MCPTool]: List of Linux diagnostic tools including:
            - System info tools (CPU, memory, disk, OS details)
            - Service management tools (list, status, logs)
            - Process management tools
            - Log reading tools (journal, audit, file)
            - Network diagnostic tools
            - Storage and hardware tools
    
    Raises:
        ValueError: If the server path does not exist.
        Exception: If connection to the MCP server fails.
    
    Example:
        ```python
        # Basic usage with default path
        tools = await create_linux_tools()
        
        # With custom server path and log access
        tools = await create_linux_tools(
            server_path="/path/to/linux-mcp-server",
            allowed_log_paths="/var/log/messages,/var/log/secure"
        )
        
        # Use in agent
        agent = RequirementAgent(
            tools=[*tools, ThinkTool()],
            ...
        )
        ```
    """
    # Default to ~/development/linux-mcp-server if no path provided
    if server_path is None:
        server_path = str(Path.home() / "development" / "linux-mcp-server")
    
    # Validate server path exists
    server_path_obj = Path(server_path)
    if not server_path_obj.exists():
        raise ValueError(
            f"Linux MCP server path does not exist: {server_path}\n"
            f"Please ensure the linux-mcp-server is installed at this location."
        )
    
    # Find the Python interpreter in the linux-mcp-server's venv
    venv_python = server_path_obj / ".venv" / "bin" / "python"
    if not venv_python.exists():
        raise ValueError(
            f"Linux MCP server venv not found at: {venv_python}\n"
            f"Please ensure the linux-mcp-server is properly installed with:\n"
            f"  cd {server_path}\n"
            f"  uv venv\n"
            f"  source .venv/bin/activate\n"
            f"  uv pip install -e ."
        )
    
    # Build environment variables
    env = None
    if allowed_log_paths:
        # Copy current environment and add log paths
        env = os.environ.copy()
        env["LINUX_MCP_ALLOWED_LOG_PATHS"] = allowed_log_paths
    
    # Create the MCP client using stdio transport
    # Use the linux-mcp-server's venv Python to run the module
    server_params = StdioServerParameters(
        command=str(venv_python),
        args=[
            "-m",
            "linux_mcp_server",
        ],
        cwd=str(server_path_obj),  # Run from server directory
        env=env,  # Pass environment variables
    )
    
    # Create the stdio client (async context manager)
    client = stdio_client(server_params)
    
    # Create tools from the client
    # This will connect to the server and list all available tools
    tools = await MCPTool.from_client(client)
    
    return tools

