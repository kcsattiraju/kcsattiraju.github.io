
from sqlalchemy import text
from sqlalchemy.orm import Session

MAX_HISTORY_MESSAGES = 10


def list_conversations(db: Session):
    """List saved conversations, newest activity first, for local UI navigation."""
    return db.execute(text("""
        SELECT c.id,
            (SELECT content FROM chat_messages
             WHERE conversation_id = c.id AND role = 'user'
             ORDER BY created_at, id LIMIT 1) AS title,
            MAX(m.created_at) AS updated_at
        FROM conversations c
        JOIN chat_messages m ON m.conversation_id = c.id
        GROUP BY c.id
        ORDER BY MAX(m.created_at) DESC, c.id
    """)).mappings().all()


def get_conversation_history(db: Session, session_id: str):
    """Load every saved message in chronological order for display."""
    rows = db.execute(text("""
        SELECT role, content FROM chat_messages
        WHERE conversation_id = :session_id
        ORDER BY created_at, id
    """), {"session_id": session_id}).mappings().all()
    return [dict(row) for row in rows]


def get_recent_history(db: Session, session_id: str):
    """Retrieve recent conversation messages."""

    rows = db.execute(
        text("""
            SELECT role, content
            FROM chat_messages
            WHERE conversation_id = :session_id
            ORDER BY created_at DESC, id DESC
            LIMIT :limit
        """),
        {
            "session_id": session_id,
            "limit": MAX_HISTORY_MESSAGES
        }
    ).mappings().all()

    # Convert to chronological order
    return [
        {
            "role": row["role"],
            "content": row["content"]
        }
        for row in reversed(rows)
    ]


def save_conversation_messages(
    db: Session,
    session_id: str,
    user_message: str,
    assistant_message: str
):
    """Persist a user and assistant exchange."""

    try:
        # Ensure conversation exists
        db.execute(
            text("""
                INSERT INTO conversations (id, created_at)
                VALUES (:session_id, NOW())
                ON CONFLICT (id) DO NOTHING
            """),
            {"session_id": session_id}
        )

        # Save user message
        db.execute(
            text("""
                INSERT INTO chat_messages
                    (conversation_id, role, content, created_at)
                VALUES
                    (:session_id, 'user', :content, NOW())
            """),
            {
                "session_id": session_id,
                "content": user_message
            }
        )

        # Save assistant message
        db.execute(
            text("""
                INSERT INTO chat_messages
                    (conversation_id, role, content, created_at)
                VALUES
                    (:session_id, 'assistant', :content, NOW())
            """),
            {
                "session_id": session_id,
                "content": assistant_message
            }
        )

        db.commit()

    except Exception:
        db.rollback()
        raise
