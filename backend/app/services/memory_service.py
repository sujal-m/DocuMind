from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from backend.app.database.repositories.conversation_repo import ConversationRepository
from backend.app.models import Message

class MemoryService:
    def __init__(self, db: Session, window_size: int = 6):
        self.db = db
        self.conv_repo = ConversationRepository(db)
        self.window_size = window_size

    def get_conversation_context(self, conversation_id: str) -> Tuple[List[Dict[str, str]], str]:
        """
        Retrieves sliding-window conversation history for LLM prompting.
        Returns:
            (formatted_messages, running_summary)
        """
        if not conversation_id:
            return [], ""

        all_msgs = self.conv_repo.get_messages(conversation_id, limit=100)
        if not all_msgs:
            return [], ""

        # If total turns exceed window, summarize older turns
        if len(all_msgs) > self.window_size:
            older_msgs = all_msgs[:-self.window_size]
            recent_msgs = all_msgs[-self.window_size:]

            summary_points = []
            for m in older_msgs:
                role = "User" if m.sender == "user" else "Assistant"
                summary_points.append(f"{role}: {m.content[:100]}...")
            running_summary = "Prior conversation context summary:\n" + "\n".join(summary_points[-4:])
        else:
            recent_msgs = all_msgs
            running_summary = ""

        formatted_messages = []
        for m in recent_msgs:
            formatted_messages.append({
                "role": "user" if m.sender == "user" else "model",
                "content": m.content
            })

        return formatted_messages, running_summary
