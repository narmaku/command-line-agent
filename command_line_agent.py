#!/usr/bin/env python3
"""Command-line entry point for the troubleshooting agent."""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Set up logging before anything else
from config.logging_config import setup_logging, suppress_beeai_console_output, is_debug_mode, install_print_filter
setup_logging()
suppress_beeai_console_output()
install_print_filter()

# Configure Ollama endpoint BEFORE importing BeeAI/Ollama modules
if os.getenv("LLM_PROVIDER", "watsonx").lower() == "ollama":
    ollama_base_url = os.getenv("OLLAMA_BASE_URL")
    if ollama_base_url:
        os.environ["OLLAMA_HOST"] = ollama_base_url
        if is_debug_mode():
            print(f"🔧 Configured Ollama endpoint: {ollama_base_url}")
    elif is_debug_mode():
        print("🔧 Using default Ollama endpoint: http://localhost:11434")

from agent import run_agent


if __name__ == "__main__":
    asyncio.run(run_agent())