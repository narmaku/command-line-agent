"""Tests for the main troubleshooting agent."""
import os
from unittest.mock import patch
import pytest


class TestTroubleshootingAgent:
    """Test the system troubleshooting agent."""

    @pytest.mark.asyncio
    async def test_agent_initialization_with_valid_env(self):
        """Test that agent initializes with correct configuration."""
        with patch.dict(os.environ, {
            'WATSONX_API_KEY': 'test_key',
            'WATSONX_PROJECT_ID': 'test_project',
            'WATSONX_URL': 'https://test.com',
            'POSTGRES_HOST': 'localhost',
            'POSTGRES_PORT': '5432',
            'POSTGRES_DB': 'rag_db',
            'POSTGRES_USER': 'user',
            'POSTGRES_PASSWORD': 'pass'
        }):
            from main import create_troubleshooting_agent
            
            # Agent should initialize but may fail to connect to RAG (expected)
            agent = await create_troubleshooting_agent()
            
            assert agent is not None
            assert agent._meta.name == "SystemTroubleshootingAgent"
            # Should have at least ThinkTool
            assert len(agent._tools) > 0

    @pytest.mark.asyncio
    async def test_agent_graceful_degradation_without_rag(self):
        """Test that agent works without RAG database connection."""
        with patch.dict(os.environ, {
            'WATSONX_API_KEY': 'test_key',
            'WATSONX_PROJECT_ID': 'test_project',
            'WATSONX_URL': 'https://test.com'
        }, clear=True):
            from main import create_troubleshooting_agent
            
            # Should create agent with just ThinkTool (RAG will fail gracefully)
            agent = await create_troubleshooting_agent()
            
            assert agent is not None
            # Should have at least one tool (ThinkTool)
            assert len(agent._tools) >= 1
            assert any('think' in tool.name.lower() for tool in agent._tools)

    @pytest.mark.asyncio
    async def test_agent_has_correct_tools(self):
        """Test that agent has the expected tools."""
        with patch.dict(os.environ, {
            'WATSONX_API_KEY': 'test_key',
            'WATSONX_PROJECT_ID': 'test_project',
            'WATSONX_URL': 'https://test.com'
        }, clear=True):
            from main import create_troubleshooting_agent
            
            agent = await create_troubleshooting_agent()
            
            # Verify tools are present
            tool_names = [tool.name.lower() for tool in agent._tools]
            assert 'think' in tool_names
            # RAG tool may or may not be present depending on DB connectivity

