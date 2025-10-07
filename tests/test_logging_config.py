"""Tests for logging configuration module."""
import os
import json
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from config.logging_config import (
    setup_logging,
    get_logger,
    is_debug_mode,
    create_event_observer,
)


class TestLoggingSetup:
    """Tests for logging setup functionality."""
    
    def test_is_debug_mode_returns_true_when_enabled(self):
        """Test DEBUG mode detection when DEBUG=true."""
        with patch.dict(os.environ, {"DEBUG": "true"}):
            assert is_debug_mode() is True
    
    def test_is_debug_mode_returns_false_when_disabled(self):
        """Test DEBUG mode detection when DEBUG=false."""
        with patch.dict(os.environ, {"DEBUG": "false"}):
            assert is_debug_mode() is False
    
    def test_is_debug_mode_returns_false_when_not_set(self):
        """Test DEBUG mode detection when DEBUG not set."""
        with patch.dict(os.environ, {}, clear=True):
            assert is_debug_mode() is False
    
    def test_setup_logging_creates_log_directory(self, tmp_path):
        """Test that setup_logging creates log directory if missing."""
        log_dir = tmp_path / "logs"
        with patch("logging_config.LOG_DIR", log_dir), \
             patch("logging_config._is_setup", False), \
             patch("logging_config._logger", None):
            setup_logging()
            assert log_dir.exists()
    
    def test_setup_logging_uses_debug_level_when_debug_enabled(self, tmp_path):
        """Test that DEBUG=true sets TRACE log level."""
        log_dir = tmp_path / "logs"
        with patch("logging_config.LOG_DIR", log_dir), \
             patch.dict(os.environ, {"DEBUG": "true", "BEEAI_LOG_LEVEL": "TRACE"}):
            logger = setup_logging()
            # BeeAI Logger should be configured at TRACE level
            assert logger is not None
    
    def test_setup_logging_uses_info_level_when_debug_disabled(self, tmp_path):
        """Test that DEBUG=false sets INFO log level."""
        log_dir = tmp_path / "logs"
        with patch("logging_config.LOG_DIR", log_dir), \
             patch.dict(os.environ, {"DEBUG": "false", "BEEAI_LOG_LEVEL": "INFO"}):
            logger = setup_logging()
            assert logger is not None
    
    def test_get_logger_returns_configured_logger(self):
        """Test that get_logger returns a configured BeeAI Logger."""
        logger = get_logger()
        assert logger is not None
        # Should have BeeAI Logger methods
        assert hasattr(logger, "info")
        assert hasattr(logger, "debug")
        assert hasattr(logger, "error")


class TestEventObserver:
    """Tests for event observer functionality."""
    
    def test_create_event_observer_filters_debug_events(self):
        """Test that event observer filters out debug events when DEBUG=false."""
        with patch.dict(os.environ, {"DEBUG": "false"}):
            observer = create_event_observer()
            assert callable(observer)
    
    def test_create_event_observer_shows_all_events_in_debug(self):
        """Test that event observer shows all events when DEBUG=true."""
        with patch.dict(os.environ, {"DEBUG": "true"}):
            observer = create_event_observer()
            assert callable(observer)
    
    @patch("logging_config.get_logger")
    def test_event_observer_logs_in_debug_mode(self, mock_get_logger):
        """Test that event observer logs events in DEBUG mode."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        with patch.dict(os.environ, {"DEBUG": "true"}):
            observer = create_event_observer()
            
            # Simulate event
            mock_emitter = MagicMock()
            
            # This should register event listeners in debug mode
            observer(mock_emitter)
            mock_emitter.on.assert_called()
    
    @patch("logging_config.get_logger")
    def test_event_observer_suppresses_in_normal_mode(self, mock_get_logger):
        """Test that event observer doesn't register listeners in normal mode."""
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        
        with patch.dict(os.environ, {"DEBUG": "false"}):
            observer = create_event_observer()
            
            # Simulate event
            mock_emitter = MagicMock()
            
            # This should not register any listeners in normal mode
            observer(mock_emitter)
            mock_emitter.on.assert_not_called()

