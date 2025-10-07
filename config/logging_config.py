"""Logging configuration module with structured file logging and DEBUG toggle.

This module provides:
- Structured file logging with readable format
- Clean console output based on DEBUG flag
- BeeAI Logger configuration through environment variables
- Multiline message support
"""
import os
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Callable

# Configuration constants
LOG_DIR = Path("logs")
DEBUG_ENV_VAR = "DEBUG"
BEEAI_LOG_LEVEL_ENV_VAR = "BEEAI_LOG_LEVEL"


def get_log_file() -> Path:
    """Get the log file path for today.
    
    Returns:
        Path: Log file path.
    """
    return LOG_DIR / f"agent_{datetime.now().strftime('%Y%m%d')}.log"

# Global logger instance
_logger: logging.Logger | None = None
_is_setup: bool = False


def is_debug_mode() -> bool:
    """Check if DEBUG mode is enabled via environment variable.
    
    Returns:
        bool: True if DEBUG=true, False otherwise.
    """
    return os.getenv(DEBUG_ENV_VAR, "false").lower() == "true"


def setup_logging() -> logging.Logger:
    """Set up logging with structured file handler and DEBUG mode configuration.
    
    Configures:
    - BeeAI Logger level through environment variable
    - File handler for structured JSON logging
    - Console output suppression based on DEBUG flag
    
    Returns:
        logging.Logger: Configured Python logger instance.
    """
    global _logger, _is_setup
    
    if _is_setup and _logger is not None:
        return _logger
    
    # Create log directory if it doesn't exist
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Determine log level based on DEBUG flag
    debug_mode = is_debug_mode()
    log_level_str = "TRACE" if debug_mode else "INFO"
    python_log_level = logging.DEBUG if debug_mode else logging.INFO
    
    # Set environment variable for BeeAI Logger (it will read this)
    os.environ[BEEAI_LOG_LEVEL_ENV_VAR] = log_level_str
    
    # Create Python logger
    _logger = logging.getLogger("command-line-agent")
    _logger.setLevel(logging.DEBUG)  # Always log everything to handlers
    
    # Remove existing handlers to avoid duplicates
    _logger.handlers.clear()
    
    # Add file handler for structured logging
    log_file = get_log_file()
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Log everything to file
    
    # Create a readable formatter with multiline support
    class MultilineFormatter(logging.Formatter):
        """Custom formatter that handles multiline messages properly."""
        
        def format(self, record: logging.LogRecord) -> str:
            """Format log record with proper multiline handling."""
            # Format the main record
            formatted = super().format(record)
            
            # Handle multiline messages by indenting continuation lines
            if '\n' in formatted:
                lines = formatted.split('\n')
                # First line stays as is, subsequent lines get indented
                formatted = lines[0] + '\n' + '\n'.join('    ' + line for line in lines[1:])
            
            return formatted
    
    # Use a clean, readable format
    log_format = '%(asctime)s | %(levelname)-8s | %(name)s:%(module)s:%(funcName)s:%(lineno)d - %(message)s'
    file_formatter = MultilineFormatter(log_format, datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    _logger.addHandler(file_handler)
    
    # In DEBUG mode, add console handler
    if debug_mode:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(python_log_level)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(module)s:%(funcName)s:%(lineno)d - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        _logger.addHandler(console_handler)
    
    _is_setup = True
    return _logger


def get_logger() -> logging.Logger:
    """Get the configured Python logger instance.
    
    Returns:
        logging.Logger: Python logger instance.
    """
    if _logger is None or not _is_setup:
        return setup_logging()
    return _logger


def create_event_observer() -> Callable:
    """Create an event observer for comprehensive agent interaction logging.
    
    The observer logs ALL agent events to file with full details when DEBUG=true.
    In normal mode, only logs are captured via event observer, console stays clean.
    
    Returns:
        Callable: Event observer function for agent.run().observe()
    """
    logger = get_logger()
    debug_mode = is_debug_mode()
    
    def event_observer(emitter):
        """Observe agent events and log them appropriately."""
        
        # Only log events in DEBUG mode
        if not debug_mode:
            return
        
        # Log ALL events to capture complete agent behavior
        def log_all_events(data, event):
            """Log every event with full context."""
            # Get event details
            event_path = event.path if hasattr(event, 'path') else 'unknown'
            creator_name = type(event.creator).__name__ if hasattr(event, 'creator') else 'unknown'
            tool_name = getattr(event.creator, 'name', creator_name) if hasattr(event, 'creator') else 'unknown'
            
            # Extract data details
            data_str = None
            if hasattr(data, '__dict__'):
                data_str = str(vars(data))
            elif isinstance(data, dict):
                data_str = str(data)
            elif data is not None:
                data_str = str(data)
            
            # Log based on event type
            if 'start' in event_path.lower():
                logger.info(f"--> 🛠️  {tool_name}[{creator_name}][start]")
                if data_str:
                    # Log full input for comprehensive tracking
                    max_length = 10000  # DEBUG mode, use higher limit
                    if len(data_str) > max_length:
                        data_preview = data_str[:max_length] + f"... (truncated, {len(data_str)} total chars)"
                    else:
                        data_preview = data_str
                    logger.info(f"    Input: {data_preview}")
            
            elif 'finish' in event_path.lower() or 'success' in event_path.lower():
                logger.info(f"<-- 🛠️  {tool_name}[{creator_name}][finish]")
                if data_str:
                    # Log full output for comprehensive tracking
                    max_length = 10000  # DEBUG mode, use higher limit
                    if len(data_str) > max_length:
                        data_preview = data_str[:max_length] + f"... (truncated, {len(data_str)} total chars)"
                    else:
                        data_preview = data_str
                    logger.info(f"    Output: {data_preview}")
            
            elif 'error' in event_path.lower() or 'fail' in event_path.lower():
                logger.error(f"❌ {tool_name}[{creator_name}][error]")
                if data_str:
                    logger.error(f"    Error: {data_str}")
            
            else:
                # Log other events at debug level
                logger.debug(f"Event: {event_path} | {tool_name} | {creator_name}")
                if data_str and len(data_str) < 500:
                    logger.debug(f"    Data: {data_str}")
        
        # Register catch-all event handler
        emitter.on("*", log_all_events)
    
    return event_observer


def suppress_beeai_console_output() -> None:
    """Suppress BeeAI framework console output when DEBUG=false.
    
    This prevents verbose framework logs from cluttering the console
    while keeping them in the log file.
    """
    if not is_debug_mode():
        # Suppress Python warnings
        import warnings
        warnings.filterwarnings('ignore')
        
        # Suppress BeeAI's internal loggers from CONSOLE ONLY (not file)
        beeai_logger = logging.getLogger("beeai_framework")
        beeai_logger.propagate = True  # Keep propagation so logs reach file handlers
        beeai_logger.setLevel(logging.DEBUG)  # Keep all logs, just filter console output
        
        # Remove only console handlers from BeeAI logger
        for handler in beeai_logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                beeai_logger.removeHandler(handler)
        
        # Suppress other verbose loggers from CONSOLE ONLY
        for logger_name in ["httpx", "httpcore", "urllib3", "mcp", "asyncio", "langchain"]:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)  # Keep all logs for file
            logger.propagate = True
            # Remove only console handlers (not file handlers)
            for handler in logger.handlers[:]:
                if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                    logger.removeHandler(handler)
        
        # For root logger: remove console handlers but keep file handlers
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Keep all logs
        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                if handler.stream in [sys.stdout, sys.stderr]:
                    root_logger.removeHandler(handler)


def print_clean_message(message: str, prefix: str = "") -> None:
    """Print a clean message to console without debug clutter.
    
    This bypasses logging and prints directly to stdout for
    clean user-facing output. Also logs to file.
    
    Args:
        message: Message to print.
        prefix: Optional prefix (e.g., emoji indicator).
    """
    # Use the original print function stored at module load
    original_print = __builtins__.get('__original_print__', print)
    if prefix:
        original_print(f"{prefix} {message}", flush=True)
        # Also log to file
        logger = get_logger()
        logger.info(f"{prefix} {message}")
    else:
        original_print(message, flush=True)
        # Also log to file
        logger = get_logger()
        logger.info(message)


def _filtered_print(*args, **kwargs):
    """Filtered print function that suppresses framework output when DEBUG=false."""
    original_print = __builtins__.get('__original_print__', print)
    
    if is_debug_mode():
        # In debug mode, print everything to console (and it gets logged via normal handlers)
        original_print(*args, **kwargs)
        return
    
    # Convert args to string to check content
    message = ' '.join(str(arg) for arg in args)
    
    # Tool execution traces and debug output - suppress completely in normal mode
    # The event observer will handle proper logging to file
    debug_patterns = [
        'handle ',
        '-->', 
        '<--', 
        '🛠️',
        '[start]:',
        '[finish]:',
        'ThinkTool[',
        'FinalAnswerTool[',
        'MCPTool[',
        'VectorStoreSearchTool[',
        'Tool[',
    ]
    
    if any(pattern in message for pattern in debug_patterns):
        # Suppress completely - event observer handles logging
        return
    
    # Use original print for allowed messages
    original_print(*args, **kwargs)


def install_print_filter() -> None:
    """Install filtered print function when DEBUG=false.
    
    This must be called early, before any modules that might use print() are imported.
    """
    import builtins
    
    # Always save original print if not already saved
    if not hasattr(builtins, '__original_print__'):
        builtins.__original_print__ = builtins.print
    
    if not is_debug_mode():
        # Install filtered print
        builtins.print = _filtered_print
    else:
        # In debug mode, ensure we're using the original print
        if hasattr(builtins, '__original_print__'):
            builtins.print = builtins.__original_print__

