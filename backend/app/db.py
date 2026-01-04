"""Database connection and query helpers using psycopg3 with connection pooling."""
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from contextlib import contextmanager
from typing import Generator, Any, List, Dict, Optional
from app.config import get_settings
from app.constants import DatabaseConfig

settings = get_settings()

# Initialize connection pool once at module level
# This provides better performance than creating new connections per request
_pool: ConnectionPool | None = None


def _get_pool() -> ConnectionPool:
    """
    Get or create the connection pool.
    
    Returns:
        ConnectionPool instance
    """
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            settings.supabase_db_url,
            min_size=DatabaseConfig.POOL_MIN_SIZE,
            max_size=DatabaseConfig.POOL_MAX_SIZE,
            kwargs={"row_factory": dict_row, "autocommit": False},
        )
    return _pool


@contextmanager
def get_db_connection() -> Generator[psycopg.Connection, None, None]:
    """
    Context manager for database connections from pool.
    
    Yields:
        psycopg.Connection: Database connection with autocommit disabled
        
    Note:
        Connection is automatically returned to pool when context exits.
        Transactions are committed on success, rolled back on exception.
    """
    pool = _get_pool()
    with pool.connection() as conn:
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise


def execute_query(
    query: str,
    params: Optional[tuple] = None,
    fetch: bool = True
) -> List[Dict[str, Any]]:
    """
    Execute a query and return results.
    
    Args:
        query: SQL query string
        params: Query parameters tuple
        fetch: Whether to fetch results
        
    Returns:
        List of result dictionaries
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall()
            return []


def execute_many(
    query: str,
    params_list: List[tuple]
) -> None:
    """
    Execute a query multiple times with different parameters.
    
    Args:
        query: SQL query string
        params_list: List of parameter tuples
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(query, params_list)


def create_conversation(user_id: str, title: str = "New Conversation") -> str:
    """
    Create a new conversation and return its ID.
    
    Args:
        user_id: User ID who owns the conversation
        title: Initial conversation title (default: "New Conversation")
    
    Returns:
        Conversation ID (UUID as string)
    """
    query = """
        INSERT INTO chat.conversations (title, user_id)
        VALUES (%s, %s)
        RETURNING id::text
    """
    result = execute_query(query, (title, user_id))
    return result[0]['id']


def add_message(
    conversation_id: str,
    role: str,
    content: str
) -> str:
    """
    Add a message to a conversation.
    
    Args:
        conversation_id: UUID of the conversation
        role: Message role (user, assistant, system)
        content: Message content
        
    Returns:
        Message ID (UUID as string)
    """
    query = """
        INSERT INTO chat.messages (conversation_id, role, content)
        VALUES (%s, %s, %s)
        RETURNING id::text
    """
    result = execute_query(query, (conversation_id, role, content))
    return result[0]['id']


def get_conversation_messages(conversation_id: str) -> List[Dict[str, Any]]:
    """
    Get all messages for a conversation, ordered by creation time.
    
    Args:
        conversation_id: UUID of the conversation
        
    Returns:
        List of message dictionaries with id, role, content, created_at
    """
    query = """
        SELECT 
            id::text,
            conversation_id::text,
            role,
            content,
            created_at
        FROM chat.messages
        WHERE conversation_id = %s
        ORDER BY created_at ASC
    """
    return execute_query(query, (conversation_id,))


def conversation_exists(conversation_id: str) -> bool:
    """
    Check if a conversation exists.
    
    Args:
        conversation_id: UUID of the conversation
        
    Returns:
        True if conversation exists
    """
    query = """
        SELECT EXISTS(
            SELECT 1 FROM chat.conversations WHERE id = %s
        ) as exists
    """
    result = execute_query(query, (conversation_id,))
    return result[0]['exists']


def conversation_belongs_to_user(conversation_id: str, user_id: str) -> bool:
    """
    Check if a conversation belongs to a given user.
    
    Args:
        conversation_id: UUID of the conversation
        user_id: User ID to check ownership against
        
    Returns:
        True if the conversation belongs to the user, False otherwise
    """
    query = """
        SELECT EXISTS(
            SELECT 1
            FROM chat.conversations
            WHERE id = %s AND user_id = %s
        ) as exists
    """
    result = execute_query(query, (conversation_id, user_id))
    return result[0]["exists"]


def list_conversations_for_user(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    List recent conversations for a user.
    
    Args:
        user_id: User ID to fetch conversations for
        limit: Maximum number of conversations to return (default: 50)
        
    Returns:
        List of conversation dictionaries with id, title, created_at, updated_at
    """
    query = """
        SELECT
            id::text,
            title,
            created_at,
            updated_at
        FROM chat.conversations
        WHERE user_id = %s
        ORDER BY updated_at DESC NULLS LAST, created_at DESC
        LIMIT %s
    """
    return execute_query(query, (user_id, limit))


def delete_conversation(conversation_id: str, user_id: str) -> bool:
    """
    Delete a conversation and all its messages (if it belongs to the user).
    
    Args:
        conversation_id: UUID of the conversation
        user_id: User ID (for ownership verification)
        
    Returns:
        True if deleted, False if not found or doesn't belong to user
    """
    query = """
        DELETE FROM chat.conversations
        WHERE id = %s AND user_id = %s
        RETURNING id
    """
    result = execute_query(query, (conversation_id, user_id))
    return len(result) > 0


def update_conversation_title(conversation_id: str, title: str) -> bool:
    """
    Update the title of a conversation.
    
    Args:
        conversation_id: UUID of the conversation
        title: New title for the conversation
        
    Returns:
        True if updated, False if not found
    """
    query = """
        UPDATE chat.conversations
        SET title = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id
    """
    result = execute_query(query, (title, conversation_id))
    return len(result) > 0

