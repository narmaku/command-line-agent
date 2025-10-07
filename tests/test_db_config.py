"""Tests for database configuration module."""
import os
from unittest.mock import patch
import pytest
from config.db_config import DatabaseConfig, get_connection_string


class TestDatabaseConfig:
    """Test DatabaseConfig class."""

    def test_database_config_from_env(self):
        """Test loading database configuration from environment variables."""
        with patch.dict(os.environ, {
            'POSTGRES_HOST': 'localhost',
            'POSTGRES_PORT': '5432',
            'POSTGRES_DB': 'rag_db',
            'POSTGRES_USER': 'testuser',
            'POSTGRES_PASSWORD': 'testpass'
        }):
            config = DatabaseConfig.from_env()
            assert config.host == 'localhost'
            assert config.port == 5432
            assert config.database == 'rag_db'
            assert config.user == 'testuser'
            assert config.password == 'testpass'

    def test_database_config_defaults(self):
        """Test default values when env vars not set."""
        with patch.dict(os.environ, {}, clear=True):
            config = DatabaseConfig.from_env()
            assert config.host == 'localhost'
            assert config.port == 5432
            assert config.database == 'rag_db'

    def test_get_connection_string(self):
        """Test connection string generation."""
        with patch.dict(os.environ, {
            'POSTGRES_HOST': 'testhost',
            'POSTGRES_PORT': '5433',
            'POSTGRES_DB': 'testdb',
            'POSTGRES_USER': 'user',
            'POSTGRES_PASSWORD': 'pass'
        }):
            conn_str = get_connection_string()
            assert 'postgresql+psycopg' in conn_str
            assert 'testhost' in conn_str
            assert '5433' in conn_str
            assert 'testdb' in conn_str
            assert 'user' in conn_str
            assert 'pass' in conn_str

    def test_get_connection_string_without_credentials(self):
        """Test connection string when credentials are not provided."""
        with patch.dict(os.environ, {
            'POSTGRES_HOST': 'localhost',
            'POSTGRES_PORT': '5432',
            'POSTGRES_DB': 'rag_db'
        }, clear=True):
            conn_str = get_connection_string()
            assert 'postgresql+psycopg' in conn_str
            assert 'localhost' in conn_str
            assert 'rag_db' in conn_str

