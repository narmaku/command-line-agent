"""Tests for LLM configuration module."""
import os
from unittest.mock import patch

import pytest

from llm_config import (
    get_llm_config,
    get_embedding_model_config,
    create_chat_model,
    get_llm_temperature,
    get_llm_max_tokens,
    get_memory_max_tokens,
    get_agent_instructions_file,
    load_agent_instructions,
)


class TestGetLLMConfig:
    """Tests for get_llm_config function."""

    def test_defaults_to_watsonx_when_no_env_vars(self):
        """Should default to WatsonX provider for backward compatibility."""
        with patch.dict(os.environ, {}, clear=True):
            provider, model = get_llm_config()
            assert provider == "watsonx"
            assert model == "ibm/granite-3-8b-instruct"

    def test_reads_openai_config_from_env(self):
        """Should read OpenAI configuration from environment variables."""
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "openai",
            "LLM_MODEL": "gpt-4"
        }):
            provider, model = get_llm_config()
            assert provider == "openai"
            assert model == "gpt-4"

    def test_reads_ollama_config_from_env(self):
        """Should read Ollama configuration from environment variables."""
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "ollama",
            "LLM_MODEL": "llama3.2"
        }):
            provider, model = get_llm_config()
            assert provider == "ollama"
            assert model == "llama3.2"

    def test_reads_gemini_config_from_env(self):
        """Should read Gemini configuration from environment variables."""
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "gemini",
            "LLM_MODEL": "gemini-pro"
        }):
            provider, model = get_llm_config()
            assert provider == "gemini"
            assert model == "gemini-pro"

    def test_uses_default_model_for_provider_when_model_not_specified(self):
        """Should use default model for provider when LLM_MODEL not set."""
        with patch.dict(os.environ, {"LLM_PROVIDER": "openai"}, clear=True):
            provider, model = get_llm_config()
            assert provider == "openai"
            assert model == "gpt-4o-mini"  # OpenAI default

    def test_supports_anthropic_provider(self):
        """Should support Anthropic as a provider."""
        with patch.dict(os.environ, {
            "LLM_PROVIDER": "anthropic",
            "LLM_MODEL": "claude-3-5-sonnet-20241022"
        }):
            provider, model = get_llm_config()
            assert provider == "anthropic"
            assert model == "claude-3-5-sonnet-20241022"


class TestGetEmbeddingModelConfig:
    """Tests for get_embedding_model_config function."""

    def test_defaults_to_watsonx_embedding_when_no_env_vars(self):
        """Should default to WatsonX embedding for backward compatibility."""
        with patch.dict(os.environ, {}, clear=True):
            provider, model = get_embedding_model_config()
            assert provider == "watsonx"
            assert model == "ibm/slate-125m-english-rtrvr-v2"

    def test_reads_openai_embedding_from_env(self):
        """Should read OpenAI embedding configuration from env."""
        with patch.dict(os.environ, {
            "EMBEDDING_PROVIDER": "openai",
            "EMBEDDING_MODEL": "text-embedding-3-small"
        }):
            provider, model = get_embedding_model_config()
            assert provider == "openai"
            assert model == "text-embedding-3-small"

    def test_reads_ollama_embedding_from_env(self):
        """Should read Ollama embedding configuration from env."""
        with patch.dict(os.environ, {
            "EMBEDDING_PROVIDER": "ollama",
            "EMBEDDING_MODEL": "nomic-embed-text"
        }):
            provider, model = get_embedding_model_config()
            assert provider == "ollama"
            assert model == "nomic-embed-text"

    def test_uses_llm_provider_as_fallback_for_embedding(self):
        """Should use LLM_PROVIDER as fallback when EMBEDDING_PROVIDER not set."""
        with patch.dict(os.environ, {"LLM_PROVIDER": "openai"}, clear=True):
            provider, model = get_embedding_model_config()
            assert provider == "openai"
            assert model == "text-embedding-3-small"  # OpenAI embedding default

    def test_uses_default_embedding_model_for_provider(self):
        """Should use default embedding model when EMBEDDING_MODEL not specified."""
        with patch.dict(os.environ, {"EMBEDDING_PROVIDER": "ollama"}, clear=True):
            provider, model = get_embedding_model_config()
            assert provider == "ollama"
            assert model == "nomic-embed-text"  # Ollama embedding default


class TestCreateChatModel:
    """Tests for create_chat_model function."""

    @patch('llm_config.ChatModel.from_name')
    def test_creates_watsonx_chat_model(self, mock_from_name):
        """Should create WatsonX chat model with correct parameters."""
        create_chat_model("watsonx", "ibm/granite-3-8b-instruct", temperature=0.7, max_tokens=2048)
        
        mock_from_name.assert_called_once()
        call_args = mock_from_name.call_args
        assert call_args[0][0] == "watsonx:ibm/granite-3-8b-instruct"

    @patch('llm_config.ChatModel.from_name')
    def test_creates_openai_chat_model(self, mock_from_name):
        """Should create OpenAI chat model with correct parameters."""
        create_chat_model("openai", "gpt-4", temperature=0.5)
        
        mock_from_name.assert_called_once()
        call_args = mock_from_name.call_args
        assert call_args[0][0] == "openai:gpt-4"

    @patch('llm_config.ChatModel.from_name')
    def test_creates_ollama_chat_model(self, mock_from_name):
        """Should create Ollama chat model with correct parameters."""
        create_chat_model("ollama", "llama3.2")
        
        mock_from_name.assert_called_once()
        call_args = mock_from_name.call_args
        assert call_args[0][0] == "ollama:llama3.2"

    @patch('llm_config.ChatModel.from_name')
    def test_creates_gemini_chat_model(self, mock_from_name):
        """Should create Gemini chat model with correct parameters."""
        create_chat_model("gemini", "gemini-pro")
        
        mock_from_name.assert_called_once()
        call_args = mock_from_name.call_args
        assert call_args[0][0] == "gemini:gemini-pro"

    @patch('llm_config.ChatModel.from_name')
    def test_passes_chat_model_parameters(self, mock_from_name):
        """Should pass ChatModelParameters to from_name."""
        create_chat_model("openai", "gpt-4", temperature=0.8, max_tokens=4096)
        
        mock_from_name.assert_called_once()
        call_args = mock_from_name.call_args
        params = call_args[0][1]
        assert params.temperature == 0.8
        assert params.max_tokens == 4096


class TestGetLLMTemperature:
    """Tests for get_llm_temperature function."""

    def test_defaults_to_0_2_when_no_env_var(self):
        """Should default to 0.2 for precise tool usage."""
        with patch.dict(os.environ, {}, clear=True):
            temp = get_llm_temperature()
            assert temp == 0.2

    def test_reads_temperature_from_env(self):
        """Should read temperature from LLM_TEMPERATURE env var."""
        with patch.dict(os.environ, {"LLM_TEMPERATURE": "0.7"}):
            temp = get_llm_temperature()
            assert temp == 0.7

    def test_clamps_temperature_to_valid_range(self):
        """Should clamp temperature to 0.0-1.0 range."""
        with patch.dict(os.environ, {"LLM_TEMPERATURE": "1.5"}):
            temp = get_llm_temperature()
            assert temp == 1.0
        
        with patch.dict(os.environ, {"LLM_TEMPERATURE": "-0.5"}):
            temp = get_llm_temperature()
            assert temp == 0.0

    def test_handles_invalid_temperature_gracefully(self):
        """Should default to 0.2 on invalid temperature value."""
        with patch.dict(os.environ, {"LLM_TEMPERATURE": "invalid"}):
            temp = get_llm_temperature()
            assert temp == 0.2


class TestGetLLMMaxTokens:
    """Tests for get_llm_max_tokens function."""

    def test_defaults_to_16000_when_no_env_var(self):
        """Should default to 16000 tokens."""
        with patch.dict(os.environ, {}, clear=True):
            max_tokens = get_llm_max_tokens()
            assert max_tokens == 16000

    def test_reads_max_tokens_from_env(self):
        """Should read max tokens from LLM_MAX_TOKENS env var."""
        with patch.dict(os.environ, {"LLM_MAX_TOKENS": "8000"}):
            max_tokens = get_llm_max_tokens()
            assert max_tokens == 8000

    def test_handles_invalid_max_tokens_gracefully(self):
        """Should default to 16000 on invalid max_tokens value."""
        with patch.dict(os.environ, {"LLM_MAX_TOKENS": "invalid"}):
            max_tokens = get_llm_max_tokens()
            assert max_tokens == 16000


class TestGetMemoryMaxTokens:
    """Tests for get_memory_max_tokens function."""

    def test_defaults_to_12000_when_no_env_var(self):
        """Should default to 12000 tokens."""
        with patch.dict(os.environ, {}, clear=True):
            max_tokens = get_memory_max_tokens()
            assert max_tokens == 12000

    def test_reads_memory_max_tokens_from_env(self):
        """Should read memory max tokens from MEMORY_MAX_TOKENS env var."""
        with patch.dict(os.environ, {"MEMORY_MAX_TOKENS": "8000"}):
            max_tokens = get_memory_max_tokens()
            assert max_tokens == 8000

    def test_handles_invalid_memory_max_tokens_gracefully(self):
        """Should default to 12000 on invalid memory_max_tokens value."""
        with patch.dict(os.environ, {"MEMORY_MAX_TOKENS": "not-a-number"}):
            max_tokens = get_memory_max_tokens()
            assert max_tokens == 12000


class TestGetAgentInstructionsFile:
    """Tests for get_agent_instructions_file function."""

    def test_defaults_to_project_agent_instructions_file(self):
        """Should default to AGENT_INSTRUCTIONS.md in project root."""
        with patch.dict(os.environ, {}, clear=True):
            instructions_file = get_agent_instructions_file()
            assert instructions_file.endswith("AGENT_INSTRUCTIONS.md")
            assert "command-line-agent" in instructions_file

    def test_reads_custom_path_from_env(self):
        """Should read custom path from AGENT_INSTRUCTIONS_FILE env var."""
        custom_path = "/custom/path/instructions.md"
        with patch.dict(os.environ, {"AGENT_INSTRUCTIONS_FILE": custom_path}):
            instructions_file = get_agent_instructions_file()
            assert instructions_file == custom_path


class TestLoadAgentInstructions:
    """Tests for load_agent_instructions function."""

    def test_loads_default_instructions_file(self):
        """Should load instructions from default AGENT_INSTRUCTIONS.md file."""
        instructions = load_agent_instructions()
        assert len(instructions) > 0
        assert "CRITICAL RULES" in instructions
        assert "troubleshooting" in instructions.lower()

    def test_raises_error_for_missing_file(self):
        """Should raise FileNotFoundError for missing instructions file."""
        with patch.dict(os.environ, {"AGENT_INSTRUCTIONS_FILE": "/nonexistent/file.md"}):
            with pytest.raises(FileNotFoundError) as exc_info:
                load_agent_instructions()
            assert "not found" in str(exc_info.value)

    def test_instructions_contain_key_sections(self):
        """Should contain all key instruction sections."""
        instructions = load_agent_instructions()
        # Check for key sections
        assert "CRITICAL RULES" in instructions
        assert "WORKFLOW" in instructions
        assert "EXAMPLE OF CORRECT RETRY BEHAVIOR" in instructions
        assert "WRONG BEHAVIOR" in instructions

