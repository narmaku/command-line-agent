"""Command-line agent for Linux system troubleshooting using AI and RAG."""
import asyncio
import os
import sys

from beeai_framework.agents.requirement import RequirementAgent
from beeai_framework.agents.requirement.requirements.conditional import ConditionalRequirement
from beeai_framework.errors import FrameworkError
from beeai_framework.memory import TokenMemory
from beeai_framework.middleware.trajectory import GlobalTrajectoryMiddleware
from beeai_framework.tools import Tool
from beeai_framework.tools.think import ThinkTool

from .config import (
    create_chat_model,
    create_event_observer,
    get_llm_config,
    get_llm_max_tokens,
    get_llm_temperature,
    get_logger,
    get_memory_max_tokens,
    is_debug_mode,
    load_agent_instructions,
    print_clean_message,
)
from .tools import create_linux_tools, create_rag_tool


async def create_troubleshooting_agent() -> RequirementAgent:
    """Create the system troubleshooting agent with RAG and filesystem capabilities.
    
    Returns:
        RequirementAgent: Configured troubleshooting agent.
    """
    # Get configured LLM provider and model
    llm_provider, llm_model = get_llm_config()
    
    # Initialize LLM with configured provider
    # Lower temperature (default 0.2) for more precise, deterministic tool usage
    llm = create_chat_model(
        provider=llm_provider,
        model=llm_model,
        temperature=get_llm_temperature(),
        max_tokens=get_llm_max_tokens(),
    )
    
    # Initialize tools list with ThinkTool
    tools = [ThinkTool()]
    
    # Add RAG tool for knowledge base access
    try:
        logger = get_logger()
        rag_tool = create_rag_tool()
        tools.append(rag_tool)
        logger.info("✅ Initialized RAG knowledge base tool")
        if is_debug_mode():
            print("✅ Initialized RAG knowledge base tool")
    except Exception as e:
        logger = get_logger()
        logger.warning(f"Could not initialize RAG tool: {e}", exc_info=True)
        if is_debug_mode():
            print(f"⚠️  Warning: Could not initialize RAG tool: {e}")
            print("   Agent will run without knowledge base access.")
    
    # Add Linux MCP tools for system diagnostics
    try:
        logger = get_logger()
        # Get Linux MCP server path from environment or use default
        linux_server_path = os.getenv("LINUX_MCP_SERVER_PATH")
        
        # Get allowed log paths from environment
        allowed_log_paths = os.getenv("LINUX_MCP_ALLOWED_LOG_PATHS")
        
        linux_tools = await create_linux_tools(
            server_path=linux_server_path,
            allowed_log_paths=allowed_log_paths
        )
        tools.extend(linux_tools)
        logger.info(f"✅ Initialized {len(linux_tools)} Linux diagnostic tools")
        if is_debug_mode():
            print(f"✅ Initialized {len(linux_tools)} Linux diagnostic tools")
    except Exception as e:
        logger = get_logger()
        logger.warning(f"Could not initialize Linux diagnostic tools: {e}", exc_info=True)
        if is_debug_mode():
            print(f"⚠️  Warning: Could not initialize Linux diagnostic tools: {e}")
            print("   Agent will run without Linux system diagnostic capabilities.")
    
    # Create memory with token management to prevent unbounded growth
    # Default 12000 tokens leaves headroom for tool outputs and responses
    memory = TokenMemory(llm=llm, max_tokens=get_memory_max_tokens())
    
    # Load agent instructions from markdown file
    try:
        instructions = load_agent_instructions()
        logger.info("✅ Loaded agent instructions from file")
        if is_debug_mode():
            print(f"✅ Loaded agent instructions ({len(instructions)} chars)")
    except Exception as e:
        logger.error(f"Failed to load agent instructions: {e}", exc_info=True)
        raise RuntimeError(f"Cannot start agent without instructions: {e}")
    
    # Create the troubleshooting agent
    agent = RequirementAgent(
        name="SystemTroubleshootingAgent",
        llm=llm,
        tools=tools,
        requirements=[ConditionalRequirement(ThinkTool, force_at_step=1)],
        role="System Troubleshooting Specialist",
        instructions=instructions,
        memory=memory,
        middlewares=[GlobalTrajectoryMiddleware(included=[Tool])],
    )
    
    return agent


async def interactive_mode(agent: RequirementAgent) -> None:
    """Run the agent in interactive mode for continuous troubleshooting.
    
    Args:
        agent: The troubleshooting agent to use.
    """
    logger = get_logger()
    
    print_clean_message("=" * 70)
    print_clean_message("System Troubleshooting Agent - Interactive Mode")
    print_clean_message("=" * 70)
    print_clean_message("Ask questions about Linux systems, logs, diagnostics, and more.")
    print_clean_message("Type 'exit' or 'quit' to end the session.\n")
    
    # Get provider and model for logging
    llm_provider, llm_model = get_llm_config()
    
    logger.info("=" * 70)
    logger.info("INTERACTIVE SESSION STARTED")
    logger.info(f"Provider: {llm_provider} | Model: {llm_model}")
    logger.info("=" * 70)
    
    interaction_count = 0
    
    while True:
        try:
            user_input = input("\n🔧 You: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['exit', 'quit', 'q']:
                print_clean_message("\n👋 Goodbye! Stay safe out there.")
                logger.info("=" * 70)
                logger.info(f"INTERACTIVE SESSION ENDED (Total interactions: {interaction_count})")
                logger.info("=" * 70)
                break
            
            interaction_count += 1
            logger.info("-" * 70)
            logger.info(f"USER QUERY #{interaction_count}")
            logger.info(f"Query: {user_input}")
            logger.info("-" * 70)
            
            print("\n🤖 Agent: ", end="", flush=True)
            
            # Create event observer for this run
            event_observer = create_event_observer()
            
            response = await agent.run(
                user_input,
                expected_output="Clear, actionable troubleshooting guidance.",
                observe=event_observer
            )
            
            agent_response = response.last_message.text
            print(agent_response)
            
            logger.info("-" * 70)
            logger.info(f"AGENT RESPONSE #{interaction_count}")
            logger.info(f"Response:\n{agent_response}")
            logger.info("-" * 70)
            
        except KeyboardInterrupt:
            print_clean_message("\n\n👋 Interrupted. Goodbye!")
            logger.info("=" * 70)
            logger.info(f"INTERACTIVE SESSION INTERRUPTED (Total interactions: {interaction_count})")
            logger.info("=" * 70)
            break
        except FrameworkError as err:
            error_msg = f"Framework Error: {err.explain()}"
            print_clean_message(f"\n❌ Error: {err.explain()}")
            logger.error(f"FRAMEWORK ERROR in interaction #{interaction_count}: {error_msg}", exc_info=True)
        except Exception as e:
            print_clean_message(f"\n❌ Unexpected error: {e}")
            logger.error(f"UNEXPECTED ERROR in interaction #{interaction_count}: {str(e)}", exc_info=True)


async def single_query_mode(agent: RequirementAgent, query: str) -> None:
    """Run a single query and exit.
    
    Args:
        agent: The troubleshooting agent to use.
        query: The query to process.
    """
    logger = get_logger()
    
    # Get provider and model for logging
    llm_provider, llm_model = get_llm_config()
    
    try:
        logger.info("=" * 70)
        logger.info("SINGLE QUERY MODE")
        logger.info(f"Provider: {llm_provider} | Model: {llm_model}")
        logger.info(f"Query: {query}")
        logger.info("=" * 70)
        
        print_clean_message(f"\n🔧 Query: {query}\n")
        print("🤖 Agent: ", end="", flush=True)
        
        # Create event observer for this run
        event_observer = create_event_observer()
        
        response = await agent.run(
            query,
            expected_output="Clear, actionable troubleshooting guidance.",
            observe=event_observer
        )
        
        agent_response = response.last_message.text
        print(agent_response)
        
        logger.info("-" * 70)
        logger.info("AGENT RESPONSE")
        logger.info(f"Response:\n{agent_response}")
        logger.info("=" * 70)
        logger.info("SINGLE QUERY MODE COMPLETED SUCCESSFULLY")
        logger.info("=" * 70)
        
    except FrameworkError as err:
        error_msg = f"Framework Error: {err.explain()}"
        print_clean_message(f"❌ Error: {err.explain()}")
        logger.error(f"FRAMEWORK ERROR: {error_msg}", exc_info=True)
        sys.exit(1)
    except Exception as e:
        print_clean_message(f"❌ Unexpected error: {e}")
        logger.error(f"UNEXPECTED ERROR: {str(e)}", exc_info=True)
        sys.exit(1)


async def run_agent(args: list[str] = None) -> None:
    """Main entry point for the command-line agent.
    
    Args:
        args: Command line arguments. If None, uses sys.argv.
    """
    if args is None:
        args = sys.argv[1:]
    
    # Get configured LLM provider and model (after .env is loaded)
    llm_provider, llm_model = get_llm_config()
    
    logger = get_logger()
    
    logger.info("=" * 70)
    logger.info("AGENT STARTUP")
    logger.info(f"LLM Provider: {llm_provider}")
    logger.info(f"LLM Model: {llm_model}")
    logger.info(f"Debug Mode: {is_debug_mode()}")
    logger.info("=" * 70)
    
    # Validate environment variables based on provider
    if llm_provider == "watsonx":
        watsonx_api_key = os.getenv("WATSONX_API_KEY")
        watsonx_project_id = os.getenv("WATSONX_PROJECT_ID")
        watsonx_url = os.getenv("WATSONX_URL")
        if not all([watsonx_api_key, watsonx_project_id, watsonx_url]):
            print_clean_message("❌ Error: Missing required WatsonX environment variables.")
            print_clean_message("Please ensure WATSONX_API_KEY, WATSONX_PROJECT_ID, and WATSONX_URL are set.")
            logger.error("Missing required WatsonX environment variables")
            sys.exit(1)
    elif llm_provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            print_clean_message("❌ Error: Missing OPENAI_API_KEY environment variable.")
            print_clean_message("Please set OPENAI_API_KEY to use OpenAI models.")
            logger.error("Missing OPENAI_API_KEY environment variable")
            sys.exit(1)
    elif llm_provider == "gemini":
        if not os.getenv("GOOGLE_API_KEY"):
            print_clean_message("❌ Error: Missing GOOGLE_API_KEY environment variable.")
            print_clean_message("Please set GOOGLE_API_KEY to use Google Gemini models.")
            logger.error("Missing GOOGLE_API_KEY environment variable")
            sys.exit(1)
    # Ollama and Anthropic don't require API keys for local/default setups
    
    if is_debug_mode():
        print_clean_message(f"🤖 Using LLM Provider: {llm_provider} with model: {llm_model}")
    
    # Create the agent
    try:
        agent = await create_troubleshooting_agent()
        logger.info("Agent initialized successfully")
    except Exception as e:
        error_msg = f"Failed to initialize agent: {e}"
        print_clean_message(f"❌ {error_msg}")
        logger.error(error_msg, exc_info=True)
        sys.exit(1)
    
    # Check for command-line arguments
    if len(args) > 0:
        # Single query mode
        query = " ".join(args)
        await single_query_mode(agent, query)
    else:
        # Interactive mode
        await interactive_mode(agent)

