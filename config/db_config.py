"""Database configuration for postgres+pgvector RAG database."""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DatabaseConfig:
    """Configuration for PostgreSQL database connection."""
    
    host: str
    port: int
    database: str
    user: Optional[str] = None
    password: Optional[str] = None

    @classmethod
    def from_env(cls) -> "DatabaseConfig":
        """Load database configuration from environment variables.
        
        Returns:
            DatabaseConfig: Configuration loaded from environment.
        """
        return cls(
            host=os.getenv("POSTGRES_HOST", "localhost"),
            port=int(os.getenv("POSTGRES_PORT", "5432")),
            database=os.getenv("POSTGRES_DB", "rag_db"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
        )


def get_connection_string() -> str:
    """Build PostgreSQL connection string for pgvector.
    
    Returns:
        str: Connection string in format postgresql+psycopg://...
    """
    config = DatabaseConfig.from_env()
    
    if config.user and config.password:
        auth = f"{config.user}:{config.password}@"
    elif config.user:
        auth = f"{config.user}@"
    else:
        auth = ""
    
    return f"postgresql+psycopg://{auth}{config.host}:{config.port}/{config.database}"

