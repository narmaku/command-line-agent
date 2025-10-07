"""LLM configuration module for multi-provider support."""
import os
from pathlib import Path
from typing import Tuple

from beeai_framework.backend import ChatModel, ChatModelParameters


# Default models for each provider
DEFAULT_MODELS = {
    "watsonx": "ibm/granite-3-8b-instruct",
    "openai": "gpt-4o-mini",
    "ollama": "llama3.2",
    "gemini": "gemini-pro",
    "anthropic": "claude-3-5-sonnet-20241022",
}

# Default embedding models for each provider
DEFAULT_EMBEDDING_MODELS = {
    "watsonx": "ibm/slate-125m-english-rtrvr-v2",
    "openai": "text-embedding-3-small",
    "ollama": "nomic-embed-text",
    "gemini": "text-embedding-004",
}


def get_llm_config() -> Tuple[str, str]:
    """Get LLM provider and model from environment variables.
    
    Returns:
        Tuple[str, str]: (provider, model) tuple.
        Defaults to WatsonX for backward compatibility.
    """
    provider = os.getenv("LLM_PROVIDER", "watsonx").lower()
    model = os.getenv("LLM_MODEL")
    
    # Use default model for provider if not specified
    if not model:
        model = DEFAULT_MODELS.get(provider, DEFAULT_MODELS["watsonx"])
    
    return provider, model


def get_embedding_model_config() -> Tuple[str, str]:
    """Get embedding model provider and model from environment variables.
    
    Falls back to LLM_PROVIDER if EMBEDDING_PROVIDER not set.
    
    Returns:
        Tuple[str, str]: (provider, model) tuple.
        Defaults to WatsonX for backward compatibility.
    """
    # Use EMBEDDING_PROVIDER if set, otherwise fall back to LLM_PROVIDER
    provider = os.getenv("EMBEDDING_PROVIDER")
    if not provider:
        provider = os.getenv("LLM_PROVIDER", "watsonx").lower()
    else:
        provider = provider.lower()
    
    model = os.getenv("EMBEDDING_MODEL")
    
    # Use default embedding model for provider if not specified
    if not model:
        model = DEFAULT_EMBEDDING_MODELS.get(
            provider, 
            DEFAULT_EMBEDDING_MODELS["watsonx"]
        )
    
    return provider, model


def get_llm_temperature() -> float:
    """Get LLM temperature from environment variable.
    
    Returns:
        float: Temperature value (0.0-1.0). Defaults to 0.2 for precise tool usage.
    """
    try:
        temp = float(os.getenv("LLM_TEMPERATURE", "0.2"))
        # Clamp to valid range
        return max(0.0, min(1.0, temp))
    except (ValueError, TypeError):
        return 0.2


def get_llm_max_tokens() -> int:
    """Get LLM max tokens from environment variable.
    
    Returns:
        int: Maximum tokens to generate. Defaults to 16000.
    """
    try:
        return int(os.getenv("LLM_MAX_TOKENS", "16000"))
    except (ValueError, TypeError):
        return 16000


def get_memory_max_tokens() -> int:
    """Get memory max tokens from environment variable.
    
    Returns:
        int: Maximum tokens for memory. Defaults to 12000.
    """
    try:
        return int(os.getenv("MEMORY_MAX_TOKENS", "12000"))
    except (ValueError, TypeError):
        return 12000


def get_agent_instructions_file() -> str:
    """Get path to agent instructions file from environment variable.
    
    Returns:
        str: Path to instructions file. Defaults to prompts/linux_diagnostics_agent.md
    """
    # Default to prompts directory (one level up from config/)
    default_path = str(Path(__file__).parent.parent / "prompts" / "linux_diagnostics_agent.md")
    return os.getenv("AGENT_INSTRUCTIONS_FILE", default_path)


def load_agent_instructions() -> str:
    """Load agent instructions from the configured markdown file.
    
    Returns:
        str: Instructions text loaded from file.
        
    Raises:
        FileNotFoundError: If the instructions file doesn't exist.
        IOError: If the file cannot be read.
    """
    instructions_file = get_agent_instructions_file()
    instructions_path = Path(instructions_file)
    
    if not instructions_path.exists():
        raise FileNotFoundError(
            f"Agent instructions file not found: {instructions_file}\n"
            f"Please ensure the file exists or set AGENT_INSTRUCTIONS_FILE environment variable."
        )
    
    try:
        return instructions_path.read_text(encoding="utf-8")
    except Exception as e:
        raise IOError(f"Failed to read instructions file {instructions_file}: {e}")


def create_chat_model(
    provider: str,
    model: str,
    temperature: float = 0.7,
    max_tokens: int = 2048,
) -> ChatModel:
    """Create a ChatModel instance for the specified provider and model.
    
    Args:
        provider: The LLM provider (e.g., 'openai', 'ollama', 'watsonx', 'gemini').
        model: The model name for that provider.
        temperature: Temperature parameter for generation.
        max_tokens: Maximum tokens to generate.
        
    Returns:
        ChatModel: Configured chat model instance.
    """
    model_name = f"{provider}:{model}"
    
    return ChatModel.from_name(
        model_name,
        ChatModelParameters(
            temperature=temperature,
            max_tokens=max_tokens,
        )
    )

