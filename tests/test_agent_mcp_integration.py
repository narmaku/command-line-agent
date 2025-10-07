"""Integration tests for agent with MCP filesystem tools."""
import os
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch, MagicMock

import pytest
from beeai_framework.tools import Tool

from agent import create_troubleshooting_agent


class TestAgentMCPIntegration:
    """Test agent integration with MCP filesystem tools."""

    @pytest.mark.asyncio
    async def test_agent_includes_filesystem_tools(self):
        """Test that the agent is created with filesystem tools."""
        with patch("main.create_chat_model") as mock_llm:
            with patch("main.create_rag_tool") as mock_rag:
                with patch("main.create_filesystem_tools") as mock_fs_tools:
                    # Setup mocks
                    mock_llm.return_value = Mock()
                    mock_rag.return_value = Mock(spec=Tool)
                    mock_filesystem_tool = Mock(spec=Tool)
                    mock_filesystem_tool.name = "read_file"
                    mock_fs_tools.return_value = [mock_filesystem_tool]
                    
                    # Create agent
                    agent = await create_troubleshooting_agent()
                    
                    # Verify filesystem tools were requested
                    mock_fs_tools.assert_called_once()
                    
                    # Verify agent has tools (should have ThinkTool + RAG + filesystem tool)
                    assert len(agent._tools) >= 3

    @pytest.mark.asyncio
    async def test_agent_graceful_degradation_without_filesystem_tools(self):
        """Test that agent works even if filesystem tools fail to initialize."""
        with patch("main.create_chat_model") as mock_llm:
            with patch("main.create_rag_tool") as mock_rag:
                with patch("main.create_filesystem_tools") as mock_fs_tools:
                    # Setup mocks
                    mock_llm.return_value = Mock()
                    mock_rag.return_value = Mock(spec=Tool)
                    # Make filesystem tools fail
                    mock_fs_tools.side_effect = Exception("MCP server unavailable")
                    
                    # Create agent should still work
                    agent = await create_troubleshooting_agent()
                    
                    # Verify agent was created without filesystem tools
                    assert agent is not None
                    # Should have at least ThinkTool and RAG tool
                    assert len(agent._tools) >= 2

    @pytest.mark.asyncio
    async def test_agent_uses_mcp_allowed_paths_env_var(self):
        """Test that agent respects MCP_ALLOWED_PATHS environment variable."""
        test_paths = "/tmp/test1,/tmp/test2"
        
        with patch("main.create_chat_model") as mock_llm:
            with patch("main.create_rag_tool") as mock_rag:
                with patch("main.create_filesystem_tools") as mock_fs_tools:
                    with patch.dict(os.environ, {"MCP_ALLOWED_PATHS": test_paths}):
                        # Setup mocks
                        mock_llm.return_value = Mock()
                        mock_rag.return_value = Mock(spec=Tool)
                        mock_fs_tool = Mock(spec=Tool)
                        mock_fs_tool.name = "read_file"
                        mock_fs_tools.return_value = [mock_fs_tool]
                        
                        # Create agent
                        agent = await create_troubleshooting_agent()
                        
                        # Verify filesystem tools were called with parsed paths
                        mock_fs_tools.assert_called_once()
                        call_args = mock_fs_tools.call_args
                        allowed_paths = call_args[1]["allowed_paths"]
                        assert allowed_paths == ["/tmp/test1", "/tmp/test2"]

    @pytest.mark.asyncio
    async def test_agent_defaults_to_home_directory_without_env_var(self):
        """Test that agent defaults to home directory when MCP_ALLOWED_PATHS not set."""
        with patch("main.create_chat_model") as mock_llm:
            with patch("main.create_rag_tool") as mock_rag:
                with patch("main.create_filesystem_tools") as mock_fs_tools:
                    # Don't clear the env completely, just ensure MCP_ALLOWED_PATHS is not set
                    env_copy = os.environ.copy()
                    env_copy.pop("MCP_ALLOWED_PATHS", None)
                    with patch.dict(os.environ, env_copy, clear=True):
                        # Setup mocks
                        mock_llm.return_value = Mock()
                        mock_rag.return_value = Mock(spec=Tool)
                        mock_fs_tool = Mock(spec=Tool)
                        mock_fs_tool.name = "list_directory"
                        mock_fs_tools.return_value = [mock_fs_tool]
                        
                        # Create agent
                        agent = await create_troubleshooting_agent()
                        
                        # Verify filesystem tools were called with None (will use default)
                        mock_fs_tools.assert_called_once()
                        call_args = mock_fs_tools.call_args
                        allowed_paths = call_args[1]["allowed_paths"]
                        assert allowed_paths is None

