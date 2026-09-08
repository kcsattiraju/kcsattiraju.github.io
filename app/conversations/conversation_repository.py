from uuid import UUID

from sqlalchemy.orm import Session

from app.conversations.conversation_model import (
    Conversation,
    Message,
)


class ConversationRepository:

    @staticmethod
    def create_conversation(
        db: Session,
        agent_id: UUID,
    ) -> Conversation:

        conversation = Conversation(
            agent_id=agent_id
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation

    @staticmethod
    def get_conversation(
        db: Session,
        conversation_id: UUID,
    ) -> Conversation | None:

        return (
            db.query(Conversation)
            .filter(
                Conversation.id
                == conversation_id
            )
            .first()
        )

    @staticmethod
    def add_message(
        db: Session,
        conversation_id: UUID,
        role: str,
        content: str,
    ) -> Message:

        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
        )

        db.add(message)
        db.commit()
        db.refresh(message)

        return message

    @staticmethod
    def get_messages(
        db: Session,
        conversation_id: UUID,
    ) -> list[Message]:

        return (
            db.query(Message)
            .filter(
                Message.conversation_id
                == conversation_id
            )
            .order_by(
                Message.created_at.asc()
            )
            .all()
        )