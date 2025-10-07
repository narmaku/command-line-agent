# Contributing to Command-Line Agent

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors. Be respectful, constructive, and professional in all interactions.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or bugfix
4. Make your changes
5. Run tests to ensure everything works
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.12 or higher
- `uv` package manager (recommended) - [Install uv](https://github.com/astral-sh/uv)
- PostgreSQL with pgvector extension (for RAG features)
- Node.js 18+ (for MCP filesystem server)
- Ollama 0.3.0+ (optional, for local models)

### Installation

**Option 1: Using uv (Recommended)**

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone your fork
git clone https://github.com/yourusername/command-line-agent.git
cd command-line-agent

# Setup with make
make sync

# Or manually
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Copy example environment file
cp .env.example .env
# Edit .env with your configuration
```

**Option 2: Using pip**

```bash
# Clone your fork
git clone https://github.com/yourusername/command-line-agent.git
cd command-line-agent

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies including dev tools
pip install -e ".[dev]"

# Copy example environment file
cp .env.example .env
# Edit .env with your configuration
```

### Environment Configuration

See `.env.example` for all available configuration options. At minimum, you'll need to set:

```bash
LLM_PROVIDER=ollama  # Or your preferred provider
LLM_MODEL=qwen2.5-coder:14b
DEBUG=true  # For development
```

## Project Structure

```
command-line-agent/
├── src/
│   └── command_line_agent/
│       ├── __init__.py
│       ├── __main__.py         # Entry point for module execution
│       ├── agent.py             # Main agent logic
│       ├── config/              # Configuration modules
│       │   ├── db_config.py
│       │   ├── llm_config.py
│       │   └── logging_config.py
│       ├── tools/               # MCP and RAG tools
│       │   ├── mcp_linux_tools.py
│       │   └── rag_integration.py
│       └── utils/               # Utility scripts
│           └── re_embed_documents.py
├── tests/                       # Test suite
├── docs/                        # Documentation
├── command_line_agent.py       # CLI entry point
├── pyproject.toml              # Project configuration
├── requirements.txt            # Dependencies
└── README.md
```

## Development Workflow

### Creating a New Feature

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the existing code structure
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   make test
   # Or: uv run pytest tests/ -v
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

   We follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` - New features
   - `fix:` - Bug fixes
   - `docs:` - Documentation changes
   - `test:` - Test additions/changes
   - `refactor:` - Code refactoring
   - `chore:` - Maintenance tasks

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Bug Fixes

1. Create an issue describing the bug (if one doesn't exist)
2. Create a branch: `git checkout -b fix/bug-description`
3. Write a failing test that reproduces the bug
4. Fix the bug
5. Ensure all tests pass
6. Submit a pull request referencing the issue

## Testing

### Running Tests

```bash
# Run all tests (using make)
make test

# Run with coverage
make test-cov

# Run all tests (using uv)
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_agent.py -v

# Run tests in debug mode
DEBUG=true uv run pytest tests/ -v -s
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Use descriptive test function names: `test_<functionality>_<scenario>`
- Use pytest fixtures for common setup
- Mock external dependencies (LLM calls, database connections, etc.)

Example:
```python
import pytest
from command_line_agent.config import get_llm_config

def test_get_llm_config_defaults():
    """Test LLM config returns defaults when env vars not set."""
    provider, model = get_llm_config()
    assert provider == "watsonx"
    assert model == "ibm/granite-3-8b-instruct"
```

## Code Style

### Python Style Guide

- Follow PEP 8 with 100 character line length
- Use type hints for function signatures
- Write docstrings for all public functions and classes
- Use descriptive variable names

### Formatting and Linting

```bash
# Format code with black
make format
# Or: uv run black src/ tests/

# Check formatting
make format-check

# Lint with ruff
make lint
# Or: uv run ruff check src/ tests/

# Fix linting issues automatically
make lint-fix
# Or: uv run ruff check --fix src/ tests/
```

### Pre-commit Checks

Before committing, run:
```bash
# Format
make format

# Lint and fix
make lint-fix

# Test
make test

# Or all at once
make format lint-fix test
```

## Submitting Changes

### Pull Request Guidelines

1. **Title**: Use a clear, descriptive title following Conventional Commits format
2. **Description**: Include:
   - What changes were made and why
   - Related issue numbers (if applicable)
   - Testing performed
   - Any breaking changes

3. **Checklist**:
   - [ ] Tests added/updated and passing
   - [ ] Documentation updated
   - [ ] Code formatted with black
   - [ ] Linting passes with ruff
   - [ ] No sensitive information in code
   - [ ] Commit messages follow Conventional Commits

### Review Process

- All PRs require at least one review
- Address review feedback promptly
- Keep PRs focused and reasonably sized
- Rebase on main if needed before merging

## Adding New LLM Providers

To add support for a new LLM provider:

1. Update `src/command_line_agent/config/llm_config.py`:
   - Add default model to `DEFAULT_MODELS`
   - Add embedding model to `DEFAULT_EMBEDDING_MODELS`
   
2. Update documentation in `README.md` and `docs/ENV_CONFIGURATION.md`

3. Add tests in `tests/test_llm_config.py`

4. Update `.env.example` with new provider configuration

## Adding New MCP Tools

To add new MCP tool integrations:

1. Create a new module in `src/command_line_agent/tools/`
2. Follow the pattern in `mcp_linux_tools.py`
3. Add integration in `src/command_line_agent/agent.py`
4. Add tests in `tests/`
5. Update documentation

## Documentation

- Keep README.md up to date with new features
- Update docs/ files for detailed configuration changes
- Include docstrings in all new code
- Add examples for complex features

## Getting Help

- Open an issue for bugs or feature requests
- Use GitHub Discussions for questions
- Check existing issues and documentation first

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

Thank you for contributing to command-line-agent! 🎉
