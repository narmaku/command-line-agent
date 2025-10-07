"""Tests for RAG integration module."""
import os
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from tools.rag_integration import create_rag_tool, get_embedding_model, create_embedding_model


class TestCreateEmbeddingModel:
    """Tests for create_embedding_model function with multiple providers."""

    @patch('command_line_agent.tools.rag_integration.EmbeddingModel.from_name')
    def test_creates_watsonx_embedding_model(self, mock_from_name):
        """Should create WatsonX embedding model."""
        create_embedding_model("watsonx", "ibm/slate-125m-english-rtrvr-v2")
        
        mock_from_name.assert_called_once_with(
            "watsonx:ibm/slate-125m-english-rtrvr-v2",
            truncate_input_tokens=500
        )

    @patch('command_line_agent.tools.rag_integration.EmbeddingModel.from_name')
    def test_creates_openai_embedding_model(self, mock_from_name):
        """Should create OpenAI embedding model."""
        create_embedding_model("openai", "text-embedding-3-small")
        
        mock_from_name.assert_called_once_with(
            "openai:text-embedding-3-small",
            truncate_input_tokens=500
        )

    @patch('command_line_agent.tools.rag_integration.EmbeddingModel.from_name')
    def test_creates_ollama_embedding_model(self, mock_from_name):
        """Should create Ollama embedding model."""
        create_embedding_model("ollama", "nomic-embed-text")
        
        mock_from_name.assert_called_once_with(
            "ollama:nomic-embed-text",
            truncate_input_tokens=500
        )

    @patch('command_line_agent.tools.rag_integration.EmbeddingModel.from_name')
    def test_creates_gemini_embedding_model(self, mock_from_name):
        """Should create Gemini embedding model."""
        create_embedding_model("gemini", "text-embedding-004")
        
        mock_from_name.assert_called_once_with(
            "gemini:text-embedding-004",
            truncate_input_tokens=500
        )


class TestRAGIntegration:
    """Test RAG integration components."""

    def test_get_embedding_model_with_watsonx(self):
        """Test embedding model initialization with watsonx credentials."""
        with patch.dict(os.environ, {
            'WATSONX_API_KEY': 'test_key',
            'WATSONX_PROJECT_ID': 'test_project',
            'WATSONX_URL': 'https://test.com'
        }):
            embedding_model = get_embedding_model()
            assert embedding_model is not None

    def test_get_embedding_model_missing_credentials(self):
        """Test that missing watsonx credentials raises an error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="WATSONX_API_KEY"):
                get_embedding_model()

    @pytest.mark.asyncio
    async def test_create_rag_tool_with_valid_config(self):
        """Test RAG tool creation with valid database configuration."""
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
            # Mock the VectorStore and VectorStoreSearchTool classes
            with patch('rag_integration.VectorStore') as mock_vector_store:
                with patch('rag_integration.VectorStoreSearchTool') as mock_tool:
                    mock_vector_store.from_name.return_value = MagicMock()
                    mock_tool_instance = MagicMock()
                    mock_tool.return_value = mock_tool_instance
                    
                    rag_tool = create_rag_tool()
                    
                    assert rag_tool is not None
                    mock_vector_store.from_name.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_rag_tool_with_missing_db_config(self):
        """Test RAG tool creation fails gracefully with missing DB config."""
        with patch.dict(os.environ, {
            'WATSONX_API_KEY': 'test_key',
            'WATSONX_PROJECT_ID': 'test_project',
            'WATSONX_URL': 'https://test.com'
        }, clear=True):
            # Should still work with defaults
            with patch('rag_integration.VectorStore') as mock_vector_store:
                with patch('rag_integration.VectorStoreSearchTool') as mock_tool:
                    mock_vector_store.from_name.return_value = MagicMock()
                    mock_tool_instance = MagicMock()
                    mock_tool.return_value = mock_tool_instance
                    
                    rag_tool = create_rag_tool()
                    
                    assert rag_tool is not None

