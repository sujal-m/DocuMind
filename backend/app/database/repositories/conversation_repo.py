from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models import Conversation, Message

class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, title: str = "New Research Session", model_name: str = "gemini-3.1-flash-lite") -> Conversation:
        conv = Conversation(title=title, model_name=model_name)
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def get_by_id(self, conversation_id: str) -> Optional[Conversation]:
        return self.db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def list_all(self, skip: int = 0, limit: int = 50) -> List[Conversation]:
        return (
            self.db.query(Conversation)
            .order_by(Conversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_title(self, conversation_id: str, title: str) -> Optional[Conversation]:
        conv = self.get_by_id(conversation_id)
        if not conv:
            return None
        conv.title = title
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def delete(self, conversation_id: str) -> bool:
        conv = self.get_by_id(conversation_id)
        if not conv:
            return False
        self.db.delete(conv)
        self.db.commit()
        return True

    def add_message(
        self,
        conversation_id: str,
        sender: str,
        content: str,
        tool_calls_json: Optional[str] = None,
        citations_json: Optional[str] = None
    ) -> Message:
        msg = Message(
            conversation_id=conversation_id,
            sender=sender,
            content=content,
            tool_calls_json=tool_calls_json,
            citations_json=citations_json
        )
        self.db.add(msg)
        # Touch conversation updated_at
        conv = self.get_by_id(conversation_id)
        if conv:
            from datetime import datetime, timezone
            conv.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_messages(self, conversation_id: str, limit: int = 50) -> List[Message]:
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(limit)
            .all()
        )

    def get_recent_messages(self, conversation_id: str, count: int = 6) -> List[Message]:
        """
        Sliding-window: returns the latest N messages in chronological order.
        """
        recent = (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(count)
            .all()
        )
        return list(reversed(recent))
