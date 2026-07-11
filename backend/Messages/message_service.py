from sqlalchemy.orm import Session
from fastapi import HTTPException
from Messages import message_repository, message_schema
from Users.user_repository import get_user_by_id

def search_users(db: Session, query: str, current_user_id: int):
    return message_repository.search_users(db, query, current_user_id)

def get_or_create_conversation(db: Session, current_user_id: int, other_user_id: int):
    if current_user_id == other_user_id:
        raise HTTPException(status_code=400, detail="Cannot start a conversation with yourself")
    
    other_user = get_user_by_id(db, other_user_id)
    if not other_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return message_repository.get_or_create_conversation(db, current_user_id, other_user_id)

def get_conversations_for_user(db: Session, user_id: int):
    conversations = message_repository.get_conversations_for_user(db, user_id)
    result = []
    for conv in conversations:
        is_user1 = conv.user1_id == user_id
        other_user = conv.user2 if is_user1 else conv.user1
        
        last_msg = db.query(message_repository.Message).filter(
            message_repository.Message.conversation_id == conv.id
        ).order_by(message_repository.Message.created_at.desc()).first()
        
        unread_count = db.query(message_repository.Message).filter(
            message_repository.Message.conversation_id == conv.id,
            message_repository.Message.sender_id != user_id,
            message_repository.Message.is_read == False
        ).count()
        
        result.append(message_schema.ConversationOut(
            id=conv.id,
            other_user_id=other_user.id,
            other_user_name=other_user.username or "User",
            last_message=last_msg.content if last_msg else None,
            unread_count=unread_count,
            created_at=conv.created_at
        ))
    return result

def get_messages_in_conversation(db: Session, conversation_id: int, user_id: int, skip: int = 0, limit: int = 50):
    conv = db.query(message_repository.Conversation).filter(message_repository.Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv.user1_id != user_id and conv.user2_id != user_id:
        raise HTTPException(status_code=403, detail="Not a participant in this conversation")
        
    return message_repository.get_messages_in_conversation(db, conversation_id, skip, limit)

def mark_messages_as_read(db: Session, conversation_id: int, user_id: int):
    conv = db.query(message_repository.Conversation).filter(message_repository.Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv.user1_id != user_id and conv.user2_id != user_id:
        raise HTTPException(status_code=403, detail="Not a participant in this conversation")
        
    message_repository.mark_messages_as_read(db, conversation_id, user_id)
    return {"status": "success"}

def create_message(db: Session, conversation_id: int, sender_id: int, content: str):
    conv = db.query(message_repository.Conversation).filter(message_repository.Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv.user1_id != sender_id and conv.user2_id != sender_id:
        raise HTTPException(status_code=403, detail="Not a participant in this conversation")
        
    return message_repository.create_message(db, conversation_id, sender_id, content)
