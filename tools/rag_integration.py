"""RAG integration for querying postgres+pgvector knowledge base."""
import os
from typing import Any

from beeai_framework.backend.embedding import EmbeddingModel
from beeai_framework.backend.vector_store import VectorStore
from beeai_framework.tools.search.retrieval import VectorStoreSearchTool

from config.db_config import get_connection_string
from config.llm_config import get_embedding_model_config


def create_embedding_model(provider: str, model: str, truncate_input_tokens: int = 500) -> EmbeddingModel:
    """Create an embedding model for the specified provider.
    
    Args:
        provider: The embedding provider (e.g., 'openai', 'ollama', 'watsonx', 'gemini').
        model: The model name for that provider.
        truncate_input_tokens: Maximum number of input tokens.
        
    Returns:
        EmbeddingModel: Configured embedding model instance.
    """
    model_name = f"{provider}:{model}"
    
    return EmbeddingModel.from_name(
        model_name,
        truncate_input_tokens=truncate_input_tokens
    )


def get_embedding_model() -> EmbeddingModel:
    """Initialize the embedding model using configured provider.
    
    Returns:
        EmbeddingModel: Configured embedding model.
        
    Raises:
        ValueError: If required environment variables are missing for watsonx (backward compatibility).
    """
    provider, model = get_embedding_model_config()
    
    # For backward compatibility, check watsonx credentials if using watsonx
    if provider == "watsonx":
        api_key = os.getenv("WATSONX_API_KEY")
        project_id = os.getenv("WATSONX_PROJECT_ID")
        url = os.getenv("WATSONX_URL")
        
        if not api_key:
            raise ValueError("WATSONX_API_KEY environment variable is required")
        if not project_id:
            raise ValueError("WATSONX_PROJECT_ID environment variable is required")
        if not url:
            raise ValueError("WATSONX_URL environment variable is required")
    
    return create_embedding_model(provider, model)


def create_rag_tool(
    collection_name: str = "knowledge_base"
) -> VectorStoreSearchTool:
    """Create a RAG tool for searching the postgres+pgvector knowledge base.
    
    Args:
        collection_name: Name of the pgvector collection/table.
        
    Returns:
        VectorStoreSearchTool: Configured RAG search tool.
    """
    embedding_model = get_embedding_model()
    connection_string = get_connection_string()
    
    # Initialize vector store using LangChain's PGVector adapter
    vector_store = VectorStore.from_name(
        name="langchain:PGVector",
        embedding_model=embedding_model,
        collection_name=collection_name,
        connection_string=connection_string,
        use_jsonb=True,
    )
    
    # Create search tool
    rag_tool = VectorStoreSearchTool(vector_store=vector_store)
    
    return rag_tool

