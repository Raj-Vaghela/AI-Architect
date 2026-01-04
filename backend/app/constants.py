"""Application-wide constants and configuration values."""


class TitleGeneration:
    """Configuration for AI-powered conversation title generation."""
    
    # OpenAI Model Configuration
    MODEL = "gpt-4o-mini"  # Fast and cost-effective for title generation
    MAX_TOKENS = 20  # Keep titles short (3-6 words typically = 10-15 tokens)
    TEMPERATURE = 0.7  # Balance between creativity and consistency
    
    # Title Length Constraints
    MAX_TITLE_LENGTH = 60  # Character limit for sidebar display
    ELLIPSIS = "..."
    TRUNCATE_AT = 57  # MAX_TITLE_LENGTH - len(ELLIPSIS) = leave room for ellipsis
    
    # Input Truncation (for prompt)
    MAX_MESSAGE_PREVIEW = 300  # Characters from user/assistant messages to include


class AgentConfig:
    """Configuration for the unified agent."""
    
    # Conversation Context
    MAX_HISTORY_MESSAGES = 10  # Number of recent messages to include in context
    MAX_ITERATIONS = 5  # Maximum ReAct loop iterations
    TEMPERATURE = 0.7  # Balance accuracy with friendly tone
    
    
class AuthConfig:
    """Configuration for JWT authentication."""
    
    # JWKS Caching
    JWKS_CACHE_TTL_SECONDS = 60.0  # How long to cache JWKS keys
    HTTP_TIMEOUT_SECONDS = 5.0  # Timeout for external HTTP requests
    
    
class DatabaseConfig:
    """Configuration for database operations."""
    
    # Connection Pooling
    POOL_MIN_SIZE = 2  # Minimum connections to maintain
    POOL_MAX_SIZE = 10  # Maximum connections allowed
    
    # Query Limits
    DEFAULT_CONVERSATION_LIMIT = 50  # Default number of conversations to return


