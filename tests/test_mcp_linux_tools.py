"""Tests for Linux MCP server integration.

This module tests the integration with the linux-mcp-server which provides
read-only Linux system diagnostic tools via the Model Context Protocol.
"""
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest


@pytest.fixture
def linux_server_path():
    """Fixture providing the path to the linux-mcp-server."""
    return "/home/nmunoz/development/linux-mcp-server"


@pytest.fixture
def mock_allowed_log_paths():
    """Fixture providing test log paths."""
    return "/var/log/messages,/var/log/secure"


class TestLinuxMCPIntegration:
    """Test suite for Linux MCP server integration."""

    @pytest.mark.asyncio
    async def test_create_linux_tools_success(self, linux_server_path):
        """Test successful creation of Linux MCP tools."""
        from mcp_linux_tools import create_linux_tools
        
        # Mock the stdio_client and MCPTool.from_client
        mock_client = MagicMock()
        mock_tools = [
            Mock(name="get_system_info"),
            Mock(name="get_cpu_info"),
            Mock(name="list_services"),
        ]
        
        with patch("mcp_linux_tools.stdio_client") as mock_stdio_client, \
             patch("mcp_linux_tools.MCPTool.from_client", new_callable=AsyncMock) as mock_from_client:
            
            mock_stdio_client.return_value = mock_client
            mock_from_client.return_value = mock_tools
            
            # Call create_linux_tools
            tools = await create_linux_tools(server_path=linux_server_path)
            
            # Verify tools were created
            assert tools is not None
            assert len(tools) == 3
            assert all(isinstance(tool, Mock) for tool in tools)
            
            # Verify stdio_client was called with correct parameters
            mock_stdio_client.assert_called_once()
            call_args = mock_stdio_client.call_args[0][0]
            
            # Check that we're running the correct command (venv python)
            assert str(call_args.command).endswith(".venv/bin/python")
            assert "-m" in call_args.args
            assert "linux_mcp_server" in call_args.args

    @pytest.mark.asyncio
    async def test_create_linux_tools_with_log_paths(self, linux_server_path, mock_allowed_log_paths):
        """Test creating Linux tools with allowed log paths."""
        from mcp_linux_tools import create_linux_tools
        
        mock_client = MagicMock()
        mock_tools = [Mock(name="get_system_info")]
        
        with patch("mcp_linux_tools.stdio_client") as mock_stdio_client, \
             patch("mcp_linux_tools.MCPTool.from_client", new_callable=AsyncMock) as mock_from_client:
            
            mock_stdio_client.return_value = mock_client
            mock_from_client.return_value = mock_tools
            
            # Call with log paths
            tools = await create_linux_tools(
                server_path=linux_server_path,
                allowed_log_paths=mock_allowed_log_paths
            )
            
            # Verify environment variable was set in server params
            call_args = mock_stdio_client.call_args[0][0]
            assert call_args.env is not None
            assert "LINUX_MCP_ALLOWED_LOG_PATHS" in call_args.env
            assert call_args.env["LINUX_MCP_ALLOWED_LOG_PATHS"] == mock_allowed_log_paths

    @pytest.mark.asyncio
    async def test_create_linux_tools_server_path_validation(self):
        """Test that invalid server path raises appropriate error."""
        from mcp_linux_tools import create_linux_tools
        
        # Test with non-existent path
        with pytest.raises(ValueError, match="Linux MCP server path does not exist"):
            await create_linux_tools(server_path="/nonexistent/path")

    @pytest.mark.asyncio
    async def test_create_linux_tools_venv_validation(self, tmp_path):
        """Test that missing venv raises appropriate error."""
        from mcp_linux_tools import create_linux_tools
        
        # Create a directory without venv
        fake_server_path = tmp_path / "linux-mcp-server"
        fake_server_path.mkdir()
        
        # Test with path that exists but has no venv
        with pytest.raises(ValueError, match="Linux MCP server venv not found"):
            await create_linux_tools(server_path=str(fake_server_path))

    @pytest.mark.asyncio
    async def test_create_linux_tools_default_server_path(self):
        """Test that default server path is used when none provided."""
        from mcp_linux_tools import create_linux_tools
        
        mock_client = MagicMock()
        mock_tools = [Mock(name="get_system_info")]
        
        # Mock Path.home() to return a test directory
        with patch("mcp_linux_tools.stdio_client") as mock_stdio_client, \
             patch("mcp_linux_tools.MCPTool.from_client", new_callable=AsyncMock) as mock_from_client, \
             patch("mcp_linux_tools.Path") as mock_path_class:
            
            # Setup mock path
            mock_home = MagicMock()
            mock_server_path = MagicMock()
            mock_server_path.exists.return_value = True
            mock_home.__truediv__.return_value = mock_server_path
            mock_path_class.home.return_value = mock_home
            
            mock_stdio_client.return_value = mock_client
            mock_from_client.return_value = mock_tools
            
            # Call without server_path
            tools = await create_linux_tools()
            
            # Verify default path was used
            mock_path_class.home.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_linux_tools_preserves_environment(self, linux_server_path):
        """Test that current environment variables are preserved."""
        from mcp_linux_tools import create_linux_tools
        
        mock_client = MagicMock()
        mock_tools = [Mock(name="get_system_info")]
        
        with patch("mcp_linux_tools.stdio_client") as mock_stdio_client, \
             patch("mcp_linux_tools.MCPTool.from_client", new_callable=AsyncMock) as mock_from_client:
            
            mock_stdio_client.return_value = mock_client
            mock_from_client.return_value = mock_tools
            
            # Call without log paths
            tools = await create_linux_tools(server_path=linux_server_path)
            
            # Verify environment is None (will inherit from current process)
            call_args = mock_stdio_client.call_args[0][0]
            # When no log paths specified, env should be None to inherit current env
            assert call_args.env is None

    @pytest.mark.asyncio
    async def test_create_linux_tools_connection_error(self, linux_server_path):
        """Test handling of connection errors."""
        from mcp_linux_tools import create_linux_tools
        
        with patch("mcp_linux_tools.stdio_client") as mock_stdio_client, \
             patch("mcp_linux_tools.MCPTool.from_client", new_callable=AsyncMock) as mock_from_client:
            
            # Simulate connection error
            mock_from_client.side_effect = Exception("Connection failed")
            
            # Should propagate the exception
            with pytest.raises(Exception, match="Connection failed"):
                await create_linux_tools(server_path=linux_server_path)


class TestLinuxMCPToolsModule:
    """Test module-level functionality."""

    def test_module_imports(self):
        """Test that module can be imported."""
        try:
            import mcp_linux_tools
            assert hasattr(mcp_linux_tools, "create_linux_tools")
        except ImportError:
            pytest.fail("Could not import mcp_linux_tools module")

    def test_module_has_required_dependencies(self):
        """Test that required dependencies are available."""
        try:
            from mcp.client.stdio import StdioServerParameters, stdio_client
            assert True
        except ImportError as e:
            pytest.fail(f"Missing required dependency: {e}")

