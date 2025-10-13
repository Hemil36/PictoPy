# This DB table contains metadata about the application and user preferences.
import json
from typing import Optional, Dict, Any
from app.database.db_utils import get_db_connection


def db_create_metadata_table() -> None:
    """Create the metadata table if it doesn't exist."""
    with get_db_connection() as conn:

        cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS metadata (
            metadata TEXT
        )
    """
    )

    # Insert initial row if table is empty
    cursor.execute("SELECT COUNT(*) FROM metadata")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO metadata (metadata) VALUES (?)", ("{}",))


def db_get_metadata() -> Optional[Dict[str, Any]]:
    """
    Get the metadata from the database.

    Returns:
        Dictionary containing metadata, or None if not found
    """
    with get_db_connection() as conn:

        cursor = conn.cursor()

    cursor.execute("SELECT metadata FROM metadata LIMIT 1")

    row = cursor.fetchone()
    if row and row[0]:
        try:
            return json.loads(row[0])
        except json.JSONDecodeError:
            return None
    return None


def db_update_metadata(metadata: Dict[str, Any]) -> bool:
    """
    Update the metadata in the database.

    Args:
        metadata: Dictionary containing metadata to store

    Returns:
        True if the metadata was updated, False otherwise
    """
    with get_db_connection() as conn:

        cursor = conn.cursor()

    metadata_json = json.dumps(metadata)

    # Delete all existing rows and insert new one
    cursor.execute("DELETE FROM metadata")
    cursor.execute("INSERT INTO metadata (metadata) VALUES (?)", (metadata_json,))

    updated = cursor.rowcount > 0
    return updated
