# Environment Variable Configuration

This document describes all available environment variables for configuring the command-line agent.

## LLM Configuration

### Core Settings

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `LLM_PROVIDER` | LLM provider to use | `watsonx` | `openai`, `ollama`, `gemini`, `anthropic` |
| `LLM_MODEL` | Model name for the provider | Provider default | `gpt-4o-mini`, `llama3.2` |
| `LLM_TEMPERATURE` | Temperature (0.0-1.0) for generation | `0.2` | `0.7` (more creative), `0.0` (deterministic) |
| `LLM_MAX_TOKENS` | Maximum tokens for LLM responses | `16000` | `8096`, `32000` |
| `MEMORY_MAX_TOKENS` | Maximum tokens for conversation memory | `12000` | `8000`, `10000` |
| `AGENT_INSTRUCTIONS_FILE` | Path to agent instructions .md file | `AGENT_INSTRUCTIONS.md` | `/custom/instructions.md` |

### Why These Defaults?

- **LLM_TEMPERATURE=0.2**: Lower temperature produces more deterministic, factual responses. This is critical for a troubleshooting agent that must:
  - Use tools correctly with proper parameter types
  - Not hallucinate data or command outputs
  - Follow instructions precisely
  
- **LLM_MAX_TOKENS=16000**: Generous token limit for complex troubleshooting scenarios with long tool outputs

- **MEMORY_MAX_TOKENS=12000**: Leaves 4000 tokens headroom for current response generation and tool outputs

### Adjusting Temperature

```bash
# More deterministic (for production troubleshooting)
LLM_TEMPERATURE=0.0

# Balanced (default - recommended)
LLM_TEMPERATURE=0.2

# More creative (for exploratory analysis)
LLM_TEMPERATURE=0.5

# High creativity (generally not recommended for troubleshooting)
LLM_TEMPERATURE=0.7
```

## Provider Credentials

### WatsonX (IBM)

```bash
LLM_PROVIDER=watsonx
LLM_MODEL=ibm/granite-3-8b-instruct
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

### OpenAI

```bash
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_api_key_here
```

Recommended models:
- `gpt-4o-mini` - Fast, cost-effective
- `gpt-4` - More capable, higher cost
- `gpt-3.5-turbo` - Budget option

### Ollama (Local)

```bash
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:14b
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_CHAT_MODEL=qwen2.5-coder:14b
```

Recommended models:
- `qwen2.5-coder:14b` - Excellent for tool calling
- `llama3.2` - General purpose
- `granite3.1:8b` - IBM's open model

### Google Gemini

```bash
LLM_PROVIDER=gemini
LLM_MODEL=gemini-pro
GOOGLE_API_KEY=your_api_key_here
```

Models:
- `gemini-pro` - Balanced
- `gemini-1.5-flash` - Fast
- `gemini-1.5-pro` - Most capable

### Anthropic (Claude)

```bash
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=your_api_key_here
```

## Embedding Models (RAG)

```bash
EMBEDDING_PROVIDER=watsonx  # Defaults to LLM_PROVIDER if not set
EMBEDDING_MODEL=ibm/slate-125m-english-rtrvr-v2
```

Defaults by provider:
- **watsonx**: `ibm/slate-125m-english-rtrvr-v2`
- **openai**: `text-embedding-3-small`
- **ollama**: `nomic-embed-text`
- **gemini**: `text-embedding-004`

## Database Configuration (RAG Vector Store)

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=command_line_agent
DB_USER=postgres
DB_PASSWORD=your_password_here

# Alternative: connection string
DB_CONNECTION_STRING=postgresql://user:password@localhost:5432/command_line_agent
```

## MCP Server Configuration

### Linux MCP Server

```bash
# Path to linux-mcp-server installation
LINUX_MCP_SERVER_PATH=/home/user/development/linux-mcp-server

# Allowed log file paths (comma-separated)
LINUX_MCP_ALLOWED_LOG_PATHS=/var/log/messages,/var/log/secure,/var/log/audit/audit.log
```

### Filesystem MCP Server

```bash
# Allowed filesystem paths (comma-separated)
MCP_ALLOWED_PATHS=/home/user,/tmp,/var/log
```

## Debug Configuration

```bash
DEBUG=true  # Enable verbose logging
```

## Example .env File

Create a `.env` file in the project root:

```bash
# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.2
LLM_MAX_TOKENS=16000
MEMORY_MAX_TOKENS=12000

# OpenAI Credentials
OPENAI_API_KEY=sk-...your-key-here...

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=command_line_agent
DB_USER=postgres
DB_PASSWORD=your_password

# MCP Servers
LINUX_MCP_SERVER_PATH=/home/user/development/linux-mcp-server
LINUX_MCP_ALLOWED_LOG_PATHS=/var/log/messages,/var/log/secure

# Debug
DEBUG=false
```

## Validation

The configuration module includes validation:

- **Temperature**: Clamped to 0.0-1.0 range
- **Tokens**: Must be valid integers, falls back to defaults on error
- **Provider**: Defaults to watsonx if not specified

## Performance Tuning

### For Faster Responses

```bash
LLM_TEMPERATURE=0.0      # Most deterministic
LLM_MAX_TOKENS=8000      # Shorter responses
MEMORY_MAX_TOKENS=6000   # Less context
```

### For Long Troubleshooting Sessions

```bash
LLM_MAX_TOKENS=32000     # If model supports it
MEMORY_MAX_TOKENS=24000  # More conversation history
```

### For Precise Tool Usage

```bash
LLM_TEMPERATURE=0.1      # Very low temperature
# Use models known for good tool calling (GPT-4, Claude, Qwen)
```

## Agent Instructions Configuration

The agent's system instructions are loaded from a markdown file, making them easy to customize without code changes.

### Default Instructions File

By default, instructions are loaded from `AGENT_INSTRUCTIONS.md` in the project root. This file contains:
- Critical rules against hallucination
- Workflow for handling tool errors
- Examples of correct and incorrect behavior
- Guidelines for staying focused on user questions

### Using Custom Instructions

To use custom instructions, create your own markdown file and set:

```bash
AGENT_INSTRUCTIONS_FILE=/path/to/custom/instructions.md
```

Your custom instructions file should maintain the same structure and key sections:
- **CRITICAL RULES** - Core behavioral constraints
- **WORKFLOW** - Step-by-step process for handling queries
- **EXAMPLES** - Concrete examples of correct behavior
- **WRONG BEHAVIOR** - What not to do

### Example: Environment-Specific Instructions

**Development environment** (more verbose, educational):
```bash
AGENT_INSTRUCTIONS_FILE=instructions/dev-instructions.md
```

**Production environment** (concise, focused):
```bash
AGENT_INSTRUCTIONS_FILE=instructions/prod-instructions.md
```

## Testing Configuration

Verify your configuration:

```bash
# Check that environment variables are loaded
uv run python -c "from llm_config import get_llm_config, get_llm_temperature, get_llm_max_tokens, load_agent_instructions; print(f'Provider: {get_llm_config()}, Temp: {get_llm_temperature()}, Max tokens: {get_llm_max_tokens()}'); print(f'Instructions: {len(load_agent_instructions())} chars')"
```

