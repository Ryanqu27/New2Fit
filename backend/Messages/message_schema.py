from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class SendMessageRequest(BaseModel):
    """Payload the frontend sends when the user hits Send."""
    conversation_id: int
    content: str

class CreateConversationRequest(BaseModel):
    """Payload the frontend sends to open/find a DM with another user."""
    other_user_id: int

class MessageOut(BaseModel):
    """A single message as returned from the DB for display in the chat window."""
    id: int
    conversation_id: int
    sender_id: int
    content: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationOut(BaseModel):
    """A conversation list item"""
    id: int
    other_user_id: int
    other_user_name: str
    last_message: Optional[str]
    unread_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSearchResult(BaseModel):
    """A user returned from the search endpoint."""
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)