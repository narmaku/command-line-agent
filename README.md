# command-line-agent

Agentic Command Line Assistant for Linux system troubleshooting using AI and RAG.

## Overview

This command-line agent uses multiple LLM providers (WatsonX, OpenAI, Ollama, Google Gemini, and more) with a postgres+pgvector RAG database to provide intelligent troubleshooting assistance for Linux systems. It can help diagnose issues, analyze logs, and provide step-by-step solutions based on proprietary knowledge stored in the RAG database.

## Features

- 🤖 **Multi-Provider AI Support**: Use WatsonX, OpenAI, Ollama (local), Google Gemini, Anthropic, or other LLM providers
- 🔧 **Flexible Configuration**: Switch between providers via environment variables
- 📚 **RAG Knowledge Base**: Queries postgres+pgvector database for precedents and solutions
- 💬 **Interactive Mode**: Continuous conversation for complex troubleshooting scenarios
- ⚡ **Single Query Mode**: Quick answers for specific questions
- 🛡️ **Graceful Degradation**: Works even when RAG database is unavailable
- ✅ **Well Tested**: Comprehensive test suite with 31 passing tests

## Installation

```bash
# Install dependencies using uv
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables. Choose one of the LLM provider configurations below:

#### Option 1: WatsonX (Default)

```bash
# LLM Provider Configuration
LLM_PROVIDER=watsonx  # Optional: defaults to watsonx
LLM_MODEL=ibm/granite-3-8b-instruct  # Optional: uses provider default if not set

# WatsonX Credentials
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://your-watsonx-url.ibm.com

# PostgreSQL + pgvector Configuration  
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_db
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```

#### Option 2: OpenAI (ChatGPT)

```bash
# LLM Provider Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini  # or gpt-4, gpt-3.5-turbo, etc.

# OpenAI Credentials
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Embedding Model (defaults to match LLM provider)
EMBEDDING_PROVIDER=openai  # Optional
EMBEDDING_MODEL=text-embedding-3-small  # Optional

# PostgreSQL + pgvector Configuration  
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_db
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```

#### Option 3: Ollama (Local Models)

```bash
# LLM Provider Configuration
LLM_PROVIDER=ollama
LLM_MODEL=llama3.2  # or granite3.3, mistral, etc.

# Ollama Configuration (no API key needed for local)
OLLAMA_BASE_URL=http://localhost:11434  # Optional: defaults to localhost

# Embedding Configuration for RAG
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text

# PostgreSQL + pgvector Configuration  
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_db
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```

#### Option 4: Google Gemini

```bash
# LLM Provider Configuration
LLM_PROVIDER=gemini
LLM_MODEL=gemini-pro  # or gemini-1.5-flash, gemini-1.5-pro, etc.

# Google Credentials
GOOGLE_API_KEY=your_google_api_key_here

# Embedding Configuration
EMBEDDING_PROVIDER=gemini
EMBEDDING_MODEL=text-embedding-004

# PostgreSQL + pgvector Configuration  
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_db
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```

#### Option 5: Anthropic Claude

```bash
# LLM Provider Configuration
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022  # or other Claude models

# Anthropic Credentials
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Note: Use OpenAI or Ollama for embeddings as Anthropic doesn't provide embedding models
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small

# PostgreSQL + pgvector Configuration  
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_db
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```

### PostgreSQL + pgvector Setup

The agent expects a PostgreSQL database with pgvector extension. You can start one using Docker:

```bash
docker run -d \
  --name rag-postgres \
  -e POSTGRES_USER=your_username \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=rag_db \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

## Usage

### Interactive Mode

Start a continuous troubleshooting session:

```bash
python main.py
```

Or with uv:

```bash
uv run python main.py
```

Then ask questions:
```
🔧 You: Why is my server running out of memory?
🤖 Agent: [Provides troubleshooting guidance...]

🔧 You: How do I analyze system logs?
🤖 Agent: [Provides log analysis steps...]
```

Type `exit`, `quit`, or `q` to end the session.

### Single Query Mode

Get a quick answer to a specific question:

```bash
python main.py "What causes high CPU usage on Linux?"
```

Or with uv:

```bash
uv run python main.py "What causes high CPU usage on Linux?"
```

## Testing

Run the complete test suite:

```bash
# Using uv
uv run pytest tests/ -v

# Using pytest directly
pytest tests/ -v
```

Run specific test modules:

```bash
uv run pytest tests/test_agent.py -v           # Agent tests
uv run pytest tests/test_db_config.py -v       # Database config tests
uv run pytest tests/test_rag_integration.py -v # RAG integration tests
```

## Project Structure

```
command-line-agent/
├── main.py                 # Main CLI application
├── llm_config.py          # Multi-provider LLM configuration
├── db_config.py           # PostgreSQL database configuration
├── rag_integration.py     # RAG tool for knowledge base queries
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (not in git)
├── tests/                 # Test suite
│   ├── test_agent.py
│   ├── test_db_config.py
│   ├── test_llm_config.py
│   └── test_rag_integration.py
└── README.md
```

## Architecture

The agent follows a modular architecture:

1. **Main Agent** (`main.py`): RequirementAgent configured for system troubleshooting
2. **LLM Configuration** (`llm_config.py`): Multi-provider LLM and embedding model configuration
3. **Database Config** (`db_config.py`): Manages PostgreSQL connection configuration
4. **RAG Integration** (`rag_integration.py`): VectorStoreSearchTool for querying knowledge base
5. **Multi-Provider Backend**: Supports WatsonX, OpenAI, Ollama, Gemini, Anthropic, and more
6. **BeeAI Framework**: Provides the agent orchestration layer with built-in provider support

## Troubleshooting

### LLM Provider Issues

#### WatsonX Authentication

If you see WatsonX authentication errors:
- Verify your `WATSONX_API_KEY` is correct
- Ensure you have proper permissions in the IBM Cloud project
- Check that the `WATSONX_PROJECT_ID` matches your project

#### OpenAI/ChatGPT Issues

If you see OpenAI errors:
- Verify your `OPENAI_API_KEY` is set and valid
- Check your OpenAI account has sufficient credits
- Ensure the model name is correct (e.g., `gpt-4o-mini`, `gpt-4`)

#### Ollama Issues

If Ollama models fail:
- Ensure Ollama is running: `ollama serve`
- Verify the model is pulled: `ollama pull llama3.2`
- Check Ollama is accessible at `http://localhost:11434`

#### Google Gemini Issues

If Gemini fails:
- Verify your `GOOGLE_API_KEY` is set and valid
- Check the model name is correct (e.g., `gemini-pro`)
- Ensure you have enabled the Gemini API in Google Cloud Console

#### Anthropic Claude Issues

If Claude fails:
- Verify your `ANTHROPIC_API_KEY` is set and valid
- Check the model name is correct
- Note: Anthropic doesn't provide embeddings; use OpenAI or Ollama for RAG

### RAG Database Connection Issues

If the RAG tool fails to initialize:
- Verify PostgreSQL is running: `docker ps | grep rag-postgres`
- Check database credentials in `.env`
- Ensure pgvector extension is installed: `psql -c "CREATE EXTENSION IF NOT EXISTS vector;"`

The agent will work without RAG but won't have access to proprietary knowledge.

## Development

This project follows Test-Driven Development (TDD) principles:

1. **RED**: Write failing tests first
2. **GREEN**: Implement code to pass tests
3. **REFACTOR**: Improve code quality

All contributions should maintain 100% test coverage for new features.

## License

See LICENSE file for details.
