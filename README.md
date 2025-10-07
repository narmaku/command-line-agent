# command-line-agent

Agentic Command Line Assistant for Linux system troubleshooting using AI and RAG.

## Overview

This command-line agent uses multiple LLM providers (WatsonX, OpenAI, Ollama, Google Gemini, and more) with a postgres+pgvector RAG database to provide intelligent troubleshooting assistance for Linux systems. It can help diagnose issues, analyze logs, and provide step-by-step solutions based on proprietary knowledge stored in the RAG database.


## Features

- 🤖 **Multi-Provider AI Support**: Use WatsonX, OpenAI, Ollama (local), Google Gemini, Anthropic, or other LLM providers
- 🔧 **Flexible Configuration**: Switch between providers via environment variables
- 📚 **RAG Knowledge Base**: Queries postgres+pgvector database for precedents and solutions
- 🐧 **Linux Diagnostics**: Comprehensive system diagnostic tools via linux-mcp-server (services, processes, logs, network, storage)
- 💬 **Interactive Mode**: Continuous conversation for complex troubleshooting scenarios
- ⚡ **Single Query Mode**: Quick answers for specific questions
- 🛡️ **Graceful Degradation**: Works even when RAG database or MCP servers are unavailable
- ✅ **Well Tested**: Comprehensive test suite with passing tests

## Requirements

### Python Dependencies
- Python 3.12+
- `uv` package manager (recommended) - [Install uv](https://github.com/astral-sh/uv)
- See `requirements.txt` or `pyproject.toml` for package dependencies

### Optional: Ollama (for local models)
- **Ollama 0.3.0 or higher** required for tool calling support
- Install/Update: `curl -fsSL https://ollama.com/install.sh | sh`
- Verify: `ollama --version` (should show 0.3.0 or higher; 0.12.3+ recommended)

### Optional: Node.js (for MCP filesystem server)
- **Node.js 18+** required for MCP filesystem tools
- The MCP filesystem server runs automatically via `npx`
- No manual installation needed - `npx` will handle it automatically

## Installation

### Quick Start with uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/yourusername/command-line-agent.git
cd command-line-agent

# Create virtual environment and install with dev dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Or use the Makefile
make sync
```

### Alternative: Using pip

```bash
# Clone the repository
git clone https://github.com/yourusername/command-line-agent.git
cd command-line-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the package in development mode
pip install -e ".[dev]"
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

#### Option 3: Ollama (Local or Remote)

```bash
# LLM Provider Configuration
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:14b  # Recommended: use larger models for better tool calling
# Other good options: llama3.1:70b, granite3.1:8b, mistral-nemo

# Ollama Configuration
# REQUIRED environment variables for BeeAI + litellm:
OLLAMA_BASE_URL=http://192.168.0.151:11434  # Your Ollama server IP/hostname
OLLAMA_API_BASE=http://192.168.0.151:11434  # Required for litellm (same as BASE_URL)
OLLAMA_CHAT_MODEL=qwen2.5-coder:14b  # Must match LLM_MODEL

# For local Ollama, use:
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_API_BASE=http://localhost:11434
# OLLAMA_CHAT_MODEL=qwen2.5-coder:14b

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

**Note:** Small models like `llama3.2:3b` may not support tool calling well. For best results with Ollama, use:
- **Recommended:** `qwen2.5:14b`, `llama3.1:70b`, `granite3.1:8b`
- **Minimum:** Models with 7B+ parameters that support function calling

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

### MCP Filesystem Configuration

The agent uses the Model Context Protocol (MCP) to provide filesystem access tools. This allows the AI agent to read files on your system for troubleshooting.

#### Configuration Options

By default, the agent has access to your home directory. You can customize allowed paths using the `MCP_ALLOWED_PATHS` environment variable:

```bash
# Allow access to specific directories (comma-separated)
MCP_ALLOWED_PATHS=/var/log,/etc,/home/user/projects

# Or allow access to home directory only (default)
# MCP_ALLOWED_PATHS= # Leave unset

# Allow access with tilde expansion
MCP_ALLOWED_PATHS=~/documents,~/logs
```

#### Available Filesystem Tools

Once configured, the agent will have access to these MCP tools:
- `read_file` - Read contents of a file
- `list_directory` - List files in a directory
- `get_file_info` - Get file metadata (size, permissions, etc.)
- `search_files` - Search for files by name or pattern

#### Security Note

⚠️ **Important**: The agent can only access directories you explicitly allow via `MCP_ALLOWED_PATHS`. If not set, it defaults to your home directory for safety.

#### How It Works

The MCP filesystem server runs locally via `npx` and communicates with the agent through stdio. No network connections are made, and the server only runs while the agent is active.

### Linux MCP Server Configuration

The agent integrates with the [linux-mcp-server](https://github.com/your-org/linux-mcp-server) to provide comprehensive Linux system diagnostic tools. This server offers read-only access to system information, services, processes, logs, network diagnostics, and storage details.

#### Available Diagnostic Tools

Once configured, the agent will have access to these MCP tools:

**System Information:**
- `get_system_info` - OS version, kernel, hostname, uptime
- `get_cpu_info` - CPU details and load averages
- `get_memory_info` - RAM usage and swap details
- `get_disk_usage` - Filesystem usage and mount points

**Service Management:**
- `list_services` - List all systemd services with status
- `get_service_status` - Detailed status of a specific service
- `get_service_logs` - Recent logs for a specific service

**Process Management:**
- `list_processes` - Running processes with CPU/memory usage
- `get_process_info` - Detailed information about a specific process

**Logs & Audit:**
- `get_journal_logs` - Query systemd journal with filters
- `get_audit_logs` - Read audit logs (if available)
- `read_log_file` - Read specific log file (whitelist-controlled)

**Network Diagnostics:**
- `get_network_interfaces` - Network interface information
- `get_network_connections` - Active network connections
- `get_listening_ports` - Ports listening on the system

**Storage & Hardware:**
- `list_block_devices` - Block devices and partitions
- `get_hardware_info` - Hardware details

#### Configuration Options

The Linux MCP server is configured using environment variables in your `.env` file:

```bash
# Optional: Custom path to linux-mcp-server
# If not set, defaults to ~/development/linux-mcp-server
LINUX_MCP_SERVER_PATH=/path/to/linux-mcp-server

# Optional: Comma-separated list of allowed log file paths
# Controls which log files the agent can read
LINUX_MCP_ALLOWED_LOG_PATHS=/var/log/messages,/var/log/secure,/var/log/audit/audit.log
```

#### Installation

To use the Linux diagnostic tools, you need to have the linux-mcp-server installed with its own virtual environment:

```bash
# Clone the linux-mcp-server repository
cd ~/development
git clone https://github.com/your-org/linux-mcp-server.git
cd linux-mcp-server

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

**Important**: The linux-mcp-server must have its own `.venv` directory with the package installed. The agent will automatically use the Python interpreter from `linux-mcp-server/.venv/bin/python` to run the server.

If you install the server in a different location, specify the path in your `.env` file with `LINUX_MCP_SERVER_PATH`.

#### Security Note

⚠️ **Important**: 
- All linux-mcp-server operations are **read-only**
- Log file access is controlled via whitelist (`LINUX_MCP_ALLOWED_LOG_PATHS`)
- No arbitrary command execution is possible
- Server runs locally via stdio (no network exposure)

#### How It Works

The Linux MCP server runs as a Python module from its installation directory and communicates with the agent through stdio. The server only runs while the agent is active and provides safe, read-only access to system diagnostics.

## Usage

### Interactive Mode

Start a continuous troubleshooting session:

```bash
# Using make (recommended)
make run

# Using uv
uv run python command_line_agent.py

# Or directly (if in venv)
python command_line_agent.py

# Or as a module
python -m command_line_agent
```

Then ask questions:
```
🔧 You: Why is my server running out of memory?
🤖 Agent: [Uses get_memory_info and get_process_info tools to diagnose...]

🔧 You: Can you read /var/log/syslog and tell me if there are any errors?
🤖 Agent: [Uses MCP filesystem tools to read the file and analyze it...]

🔧 You: Is the nginx service running?
🤖 Agent: [Uses get_service_status tool to check nginx...]
```

Type `exit`, `quit`, or `q` to end the session.

#### Example with Linux Diagnostics

```
🔧 You: Check if nginx is running and show me recent errors

🤖 Agent: Let me check the nginx service status and logs.

[Agent uses get_service_status("nginx") to check status]
[Agent uses get_service_logs("nginx") to retrieve recent logs]

The nginx service is active and running. However, I see some recent errors...
```

#### Example with System Analysis

```
🔧 You: Why is CPU usage so high?

🤖 Agent: I'll analyze the system for you.

[Agent uses get_cpu_info() to check CPU load]
[Agent uses list_processes() to identify high-CPU processes]

Your CPU load is 8.5 (on a 4-core system). The top consumers are:
1. process_name (PID 1234) - 45% CPU
2. another_process (PID 5678) - 30% CPU
...
```

### Single Query Mode

Get a quick answer to a specific question:

```bash
# Using make
make run-query QUERY="What causes high CPU usage on Linux?"

# Using uv
uv run python command_line_agent.py "What causes high CPU usage on Linux?"

# Or directly (if in venv)
python command_line_agent.py "What causes high CPU usage on Linux?"

# Or as a module
python -m command_line_agent "What causes high CPU usage on Linux?"
```

## Testing

Run the complete test suite:

```bash
# Using make (recommended)
make test

# Or with coverage
make test-cov

# Using uv directly
uv run pytest tests/ -v

# Using pytest directly (if in venv)
pytest tests/ -v
```

Run specific test modules:

```bash
uv run pytest tests/test_agent.py -v                    # Agent tests
uv run pytest tests/test_agent_mcp_integration.py -v    # MCP integration tests
uv run pytest tests/test_db_config.py -v                # Database config tests
uv run pytest tests/test_rag_integration.py -v          # RAG integration tests
```

## Project Structure

```
command-line-agent/
├── agent.py                     # Main agent logic
├── command_line_agent.py        # CLI entry point
├── config/                      # Configuration modules
│   ├── db_config.py            # Database configuration
│   ├── llm_config.py           # LLM provider configuration
│   └── logging_config.py       # Logging setup
├── tools/                       # MCP and RAG tools
│   ├── mcp_linux_tools.py      # Linux diagnostic tools
│   └── rag_integration.py      # RAG knowledge base
├── utils/                       # Utility scripts
│   └── re_embed_documents.py   # Re-embedding utility
├── prompts/                     # Agent prompts
│   └── linux_diagnostics_agent.md
├── tests/                       # Test suite
├── Makefile                     # Common development tasks
├── requirements.txt             # Dependencies
├── .env.example                 # Example environment configuration
├── CONTRIBUTING.md              # Contribution guidelines
└── README.md
```

## Architecture

The agent follows a modular architecture:

1. **Main Agent** (`main.py`): RequirementAgent configured for system troubleshooting
2. **LLM Configuration** (`llm_config.py`): Multi-provider LLM and embedding model configuration
3. **Database Config** (`db_config.py`): Manages PostgreSQL connection configuration
4. **RAG Integration** (`rag_integration.py`): VectorStoreSearchTool for querying knowledge base
5. **MCP Filesystem** (`mcp_filesystem.py`): Model Context Protocol integration for file system access
6. **Linux Diagnostics** (`mcp_linux_tools.py`): Linux MCP server integration for system diagnostics
7. **Multi-Provider Backend**: Supports WatsonX, OpenAI, Ollama, Gemini, Anthropic, and more
8. **BeeAI Framework**: Provides the agent orchestration layer with built-in MCP and provider support

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
- Verify the model is pulled: `ollama pull qwen2.5:14b`
- Check Ollama is accessible at `http://localhost:11434`

**Tool Calling Errors:**
If you see `ValidationError` or `Failed to produce a valid tool call`:

1. **Check Ollama Version** (Most Common Issue):
   ```bash
   ollama --version
   ```
   - **Required:** Ollama **0.3.0 or higher** for tool calling support
   - If you have `0.0.0` or older version:
     ```bash
     # Update Ollama
     curl -fsSL https://ollama.com/install.sh | sh
     
     # Verify new version
     ollama --version  # Should show 0.5.x or higher
     
     # Restart Ollama
     ollama serve
     ```

2. **Model Size** (Less Common):
   - Models with < 7B parameters may struggle with complex tool calling
   - **Solution:** Use larger models:
     ```bash
     ollama pull qwen2.5:14b
     # or
     ollama pull granite3.1:8b
     
     # Update .env
     LLM_MODEL=qwen2.5:14b
     ```

3. **Test Tool Calling:**
   ```bash
   # Run diagnostic script
   uv run python test_ollama_tools.py
   ```

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
