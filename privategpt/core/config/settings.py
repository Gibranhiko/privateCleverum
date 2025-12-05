"""
Configuration management for the PrivateGPT system.

Centralized settings with environment variable support and validation.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class LogLevel(str, Enum):
    """Available log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class EmbeddingProvider(str, Enum):
    """Available embedding providers."""
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    OPENAI = "openai"


class AIProvider(str, Enum):
    """Available AI providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


@dataclass
class DatabaseSettings:
    """Database configuration settings."""
    url: str = field(default_factory=lambda: os.getenv("DATABASE_URL"))
    echo: bool = field(default_factory=lambda: os.getenv("DATABASE_ECHO", "false").lower() == "true")
    pool_size: int = field(default_factory=lambda: int(os.getenv("DATABASE_POOL_SIZE")))
    max_overflow: int = field(default_factory=lambda: int(os.getenv("DATABASE_MAX_OVERFLOW")))


@dataclass
class AISettings:
    """AI service configuration settings."""
    provider: AIProvider = field(default_factory=lambda: AIProvider(os.getenv("AI_PROVIDER")))
    
    # Ollama settings
    ollama_url: str = field(default_factory=lambda: os.getenv("OLLAMA_URL"))
    ollama_model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL"))
    
    # OpenAI settings
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL"))
    openai_base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL"))
    
    # Anthropic settings
    anthropic_api_key: Optional[str] = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    anthropic_model: str = field(default_factory=lambda: os.getenv("ANTHROPIC_MODEL"))
    
    # Generation settings
    temperature: float = field(default_factory=lambda: float(os.getenv("AI_TEMPERATURE")))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("AI_MAX_TOKENS")))
    timeout: int = field(default_factory=lambda: int(os.getenv("AI_TIMEOUT")))


@dataclass
class EmbeddingSettings:
    """Embedding configuration settings."""
    provider: EmbeddingProvider = field(default_factory=lambda: EmbeddingProvider(os.getenv("EMBEDDING_PROVIDER")))
    
    # Ollama embedding settings
    ollama_url: str = field(default_factory=lambda: os.getenv("EMBEDDING_OLLAMA_URL"))
    ollama_model: str = field(default_factory=lambda: os.getenv("EMBEDDING_OLLAMA_MODEL"))
    
    # HuggingFace settings
    hf_model: str = field(default_factory=lambda: os.getenv("EMBEDDING_HF_MODEL"))
    hf_cache_dir: Optional[str] = field(default_factory=lambda: os.getenv("HF_CACHE_DIR"))
    
    # OpenAI embedding settings
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("EMBEDDING_OPENAI_API_KEY"))
    openai_model: str = field(default_factory=lambda: os.getenv("EMBEDDING_OPENAI_MODEL"))
    
    # General embedding settings
    chunk_size: int = field(default_factory=lambda: int(os.getenv("EMBEDDING_CHUNK_SIZE")))
    chunk_overlap: int = field(default_factory=lambda: int(os.getenv("EMBEDDING_CHUNK_OVERLAP")))
    batch_size: int = field(default_factory=lambda: int(os.getenv("EMBEDDING_BATCH_SIZE")))


@dataclass
class VectorStoreSettings:
    """Vector store configuration settings."""
    provider: str = field(default_factory=lambda: os.getenv("VECTOR_STORE_PROVIDER"))
    
    # Chroma settings
    chroma_path: str = field(default_factory=lambda: os.getenv("CHROMA_PATH"))
    chroma_collection: str = field(default_factory=lambda: os.getenv("CHROMA_COLLECTION"))
    
    # Pinecone settings (if using)
    pinecone_api_key: Optional[str] = field(default_factory=lambda: os.getenv("PINECONE_API_KEY"))
    pinecone_index: str = field(default_factory=lambda: os.getenv("PINECONE_INDEX"))
    pinecone_environment: str = field(default_factory=lambda: os.getenv("PINECONE_ENVIRONMENT"))


@dataclass
class DocumentSettings:
    """Document processing configuration settings."""
    upload_dir: str = field(default_factory=lambda: os.getenv("UPLOAD_DIR"))
    processed_dir: str = field(default_factory=lambda: os.getenv("PROCESSED_DIR"))
    allowed_extensions: List[str] = field(default_factory=lambda: os.getenv("ALLOWED_EXTENSIONS").split(","))
    max_file_size: int = field(default_factory=lambda: int(os.getenv("MAX_FILE_SIZE")))
    auto_cleanup: bool = field(default_factory=lambda: os.getenv("AUTO_CLEANUP", "true").lower() == "true")
    cleanup_days: int = field(default_factory=lambda: int(os.getenv("CLEANUP_DAYS")))


@dataclass
class SecuritySettings:
    """Security configuration settings."""
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY"))
    access_token_expire_minutes: int = field(default_factory=lambda: int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    refresh_token_expire_days: int = field(default_factory=lambda: int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")))
    allowed_hosts: List[str] = field(default_factory=lambda: os.getenv("ALLOWED_HOSTS").split(","))
    cors_origins: List[str] = field(default_factory=lambda: os.getenv("CORS_ORIGINS").split(","))


@dataclass
class ServerSettings:
    """Server configuration settings."""
    host: str = field(default_factory=lambda: os.getenv("HOST"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT")))
    workers: int = field(default_factory=lambda: int(os.getenv("WORKERS")))
    reload: bool = field(default_factory=lambda: os.getenv("RELOAD", "false").lower() == "true")
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")


@dataclass
class LoggingSettings:
    """Logging configuration settings."""
    level: LogLevel = field(default_factory=lambda: LogLevel(os.getenv("LOG_LEVEL")))
    format: str = field(default_factory=lambda: os.getenv("LOG_FORMAT"))
    file_path: Optional[str] = field(default_factory=lambda: os.getenv("LOG_FILE"))
    max_size: int = field(default_factory=lambda: int(os.getenv("LOG_MAX_SIZE")))
    backup_count: int = field(default_factory=lambda: int(os.getenv("LOG_BACKUP_COUNT")))
    json_format: bool = field(default_factory=lambda: os.getenv("LOG_JSON", "false").lower() == "true")


@dataclass 
class Settings:
    """Main configuration class containing all settings."""
    
    # Core settings
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "PrivateGPT"))
    app_version: str = field(default_factory=lambda: os.getenv("APP_VERSION", "1.0.0"))
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    
    # Component settings
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    ai: AISettings = field(default_factory=AISettings)
    embedding: EmbeddingSettings = field(default_factory=EmbeddingSettings)
    vector_store: VectorStoreSettings = field(default_factory=VectorStoreSettings)
    documents: DocumentSettings = field(default_factory=DocumentSettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)
    server: ServerSettings = field(default_factory=ServerSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    
    def __post_init__(self):
        """Validate settings and create necessary directories."""
        self._validate_settings()
        self._create_directories()
    
    def _validate_settings(self):
        """Validate configuration settings."""
        # Check for required environment variables
        required_env_vars = [
            # Add all required variable names here
            "DATABASE_URL", "OLLAMA_URL", "OLLAMA_MODEL", "SECRET_KEY", "AI_TEMPERATURE", "AI_MAX_TOKENS",
            # Add more as needed
        ]
        for var in required_env_vars:
            if os.getenv(var) is None:
                raise ValueError(f"Missing required environment variable: {var}")
        # Validate required API keys based on providers
        if self.ai.provider == AIProvider.OPENAI and not self.ai.openai_api_key:
            raise ValueError("OpenAI API key is required when using OpenAI provider")
        
        if self.ai.provider == AIProvider.ANTHROPIC and not self.ai.anthropic_api_key:
            raise ValueError("Anthropic API key is required when using Anthropic provider")
        
        if (self.embedding.provider == EmbeddingProvider.OPENAI and 
            not self.embedding.openai_api_key):
            raise ValueError("OpenAI API key is required for OpenAI embeddings")
        
        # Validate file size limits
        if self.documents.max_file_size <= 0:
            raise ValueError("Maximum file size must be positive")
        
        # Validate chunk settings
        if self.embedding.chunk_size <= self.embedding.chunk_overlap:
            raise ValueError("Chunk size must be larger than chunk overlap")
        
        # Security validations
        if self.environment == "production":
            if self.security.secret_key == "your-secret-key-change-this":
                raise ValueError("Secret key must be changed in production")
            
            if self.server.debug:
                raise ValueError("Debug mode should not be enabled in production")
    
    def _create_directories(self):
        """Create necessary directories if they don't exist."""
        directories = [
            self.documents.upload_dir,
            self.documents.processed_dir,
            self.vector_store.chroma_path,
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env_file(cls, env_file: str = ".env") -> "Settings":
        """Load settings from environment file."""
        if os.path.exists(env_file):
            from dotenv import load_dotenv
            load_dotenv(env_file)
        return cls()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary (excluding sensitive data)."""
        result = {}
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, (str, int, float, bool, list)):
                # Hide sensitive information
                if "key" in field_name.lower() or "secret" in field_name.lower():
                    result[field_name] = "***"
                else:
                    result[field_name] = field_value
            elif hasattr(field_value, '__dict__'):
                result[field_name] = {
                    k: "***" if ("key" in k.lower() or "secret" in k.lower()) else v
                    for k, v in field_value.__dict__.items()
                }
        return result


# Global settings instance
settings = Settings()