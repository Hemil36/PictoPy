"""
Database connection utilities for PictoPy.

This module provides centralized database connection management with proper
foreign key constraint enforcement and error handling.
"""

import sqlite3
from contextlib import contextmanager
from typing import Generator
from app.config.settings import DATABASE_PATH


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections with foreign key constraints enabled.

    This function ensures that:
    1. Foreign key constraints are ALWAYS enabled
    2. Automatic transaction management (commit on success, rollback on error)
    3. Proper connection cleanup

    Yields:
        sqlite3.Connection: Database connection with foreign keys enabled

    Raises:
        Exception: Any database-related errors
    """
    conn = sqlite3.connect(DATABASE_PATH)

    # CRITICAL: Enable foreign key constraints
    # This is the most important setting to fix the reported issue
    conn.execute("PRAGMA foreign_keys=ON")

    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_simple_db_connection() -> sqlite3.Connection:
    """
    Get a simple database connection with foreign keys enabled.

    WARNING: When using this function, you MUST manually handle:
    - Connection closing (conn.close())
    - Transaction management (conn.commit()/conn.rollback())
    - Error handling

    The context manager `get_db_connection()` is preferred for most use cases.

    Returns:
        sqlite3.Connection: Database connection with foreign keys enabled
    """
    conn = sqlite3.connect(DATABASE_PATH)

    # CRITICAL: Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys=ON")

    return conn


def verify_foreign_keys_enabled(conn: sqlite3.Connection) -> bool:
    """
    Verify that foreign key constraints are enabled on the connection.

    Args:
        conn: SQLite database connection

    Returns:
        bool: True if foreign keys are enabled, False otherwise
    """
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys")
    result = cursor.fetchone()
    return result is not None and result[0] == 1


def test_foreign_key_enforcement() -> bool:
    """
    Test that foreign key constraints are properly enforced.

    This creates a temporary test scenario to verify that foreign key
    violations are properly caught and rejected.

    Returns:
        bool: True if foreign keys are properly enforced, False otherwise
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Try to insert a record with an invalid foreign key
            # This should fail if foreign keys are enabled
            try:
                cursor.execute(
                    "INSERT INTO images (id, path, folder_id) VALUES (?, ?, ?)",
                    ("test_id", "test_path", "nonexistent_folder_id"),
                )
                # If we get here without an exception, foreign keys are NOT enforced
                return False
            except sqlite3.IntegrityError as e:
                # This is expected - foreign key constraint should prevent the insert
                if "foreign key constraint failed" in str(e).lower():
                    return True
                else:
                    return False

    except Exception:
        return False
