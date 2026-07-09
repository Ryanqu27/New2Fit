from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from Users.UserModel import User
from Messages.ConversationModel import Conversation
from Messages.MessageModel import Message

def search_users(db: Session, query: str, current_user_id: int, limit: int = 10):
    if not query or len(query.strip()) < 2:
        return []
        
    search_term = f"%{query.strip()}%"
    
    return db.query(User).filter(
        User.id != current_user_id, 
        User.username.ilike(search_term)
    ).limit(limit).all()


def get_or_create_conversation(db: Session, user1_id: int, user2_id: int):
    u1, u2 = min(user1_id, user2_id), max(user1_id, user2_id)
    conversation = db.query(Conversation).filter(
        Conversation.user1_id == u1,
        Conversation.user2_id == u2
    ).first()
    
    if not conversation:
        conversation = Conversation(
            user1_id=u1,
            user2_id=u2
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
    return conversation


def get_conversations_for_user(db: Session, user_id: int):
    return db.query(Conversation).filter(
        or_(
            Conversation.user1_id == user_id,
            Conversation.user2_id == user_id
        )
    ).order_by(desc(Conversation.created_at)).all()


def get_messages_in_conversation(db: Session, conversation_id: int, skip: int = 0, limit: int = 50):
    return db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(desc(Message.created_at)).offset(skip).limit(limit).all()


def create_message(db: Session, conversation_id: int, sender_id: int, content: str):
    new_msg = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=content
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.created_at = new_msg.created_at
        db.commit()
        
    return new_msg


def mark_messages_as_read(db: Session, conversation_id: int, reader_id: int):
    db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.sender_id != reader_id,
        Message.is_read == False
    ).update({"is_read": True})
    db.commit()