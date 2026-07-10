from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from database import get_db
from Users.auth import get_current_user, JWT_SECRET, JWT_ALGORITHM
import jwt
from Users.UserModel import User
from Messages import message_service, message_schema
from Messages.connection_manager import manager

router = APIRouter(
    prefix="/api/messages",
    tags=["Messages"]
)

@router.get("/users/search", response_model=list[message_schema.UserSearchResult])
def search_users(q: str = Query(..., min_length=2), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return message_service.search_users(db, q, current_user.id)

@router.post("/conversations", response_model=message_schema.ConversationOut)
def get_or_create_conversation(request: message_schema.CreateConversationRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conv = message_service.get_or_create_conversation(db, current_user.id, request.other_user_id)
    is_user1 = conv.user1_id == current_user.id
    other_user = conv.user2 if is_user1 else conv.user1
    
    return message_schema.ConversationOut(
        id=conv.id,
        other_user_id=other_user.id,
        other_user_name=other_user.first_name,
        last_message=None,
        unread_count=0,
        created_at=conv.created_at
    )

@router.get("/conversations", response_model=list[message_schema.ConversationOut])
def get_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return message_service.get_conversations_for_user(db, current_user.id)

@router.get("/conversations/{conversation_id}/messages", response_model=list[message_schema.MessageOut])
def get_messages(conversation_id: int, skip: int = 0, limit: int = 50, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return message_service.get_messages_in_conversation(db, conversation_id, current_user.id, skip, limit)

@router.post("/conversations/{conversation_id}/read")
def mark_read(conversation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return message_service.mark_messages_as_read(db, conversation_id, current_user.id)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    try:
        # Extract the token from the HttpOnly cookie rather than the query string
        token = websocket.cookies.get("access_token")
        if not token:
            await websocket.close(code=1008)
            return

        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = int(payload["sub"])
    except Exception:
        await websocket.close(code=1008)
        return

    from Users.user_repository import get_user_by_id
    user = get_user_by_id(db, user_id)
    if not user:
        await websocket.close(code=1008)
        return

    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if "conversation_id" in data and "content" in data:
                conversation_id = int(data["conversation_id"])
                content = data["content"]
                
                new_msg = message_service.create_message(db, conversation_id, user_id, content)
                
                conv_model = db.query(message_service.message_repository.Conversation).filter(
                    message_service.message_repository.Conversation.id == conversation_id
                ).first()
                if conv_model:
                    recipient_id = conv_model.user2_id if conv_model.user1_id == user_id else conv_model.user1_id
                    
                    msg_out = message_schema.MessageOut(
                        id=new_msg.id,
                        conversation_id=new_msg.conversation_id,
                        sender_id=new_msg.sender_id,
                        content=new_msg.content,
                        is_read=new_msg.is_read,
                        created_at=new_msg.created_at
                    )
                    
                    await manager.send_personal_message(msg_out.model_dump(mode="json"), user_id)
                    await manager.send_personal_message(msg_out.model_dump(mode="json"), recipient_id)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(user_id)
