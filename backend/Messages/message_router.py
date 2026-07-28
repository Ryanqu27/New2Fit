from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query, Request
from sqlalchemy.orm import Session
from database import get_db
from Users.auth import get_current_user_id, JWT_SECRET, JWT_ALGORITHM
import jwt
from Messages import message_service, message_schema
from Messages.connection_manager import manager
from limiter import limiter

router = APIRouter(
    prefix="/api/messages",
    tags=["Messages"]
)

@router.get("/users/search", response_model=list[message_schema.UserSearchResult])
@limiter.limit("30/minute")
def search_users(request: Request, q: str = Query(..., min_length=2), user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return message_service.search_users(db, q, user_id)

@router.post("/conversations", response_model=message_schema.ConversationOut)
@limiter.limit("20/minute")
def get_or_create_conversation(request: Request, body: message_schema.CreateConversationRequest, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    conv = message_service.get_or_create_conversation(db, user_id, body.other_user_id)
    is_user1 = conv.user1_id == user_id
    other_user = conv.user2 if is_user1 else conv.user1
    
    return message_schema.ConversationOut(
        id=conv.id,
        other_user_id=other_user.id,
        other_user_name=other_user.username or "User",
        last_message=None,
        unread_count=0,
        created_at=conv.created_at
    )

@router.get("/conversations", response_model=list[message_schema.ConversationOut])
@limiter.limit("60/minute")
def get_conversations(request: Request, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return message_service.get_conversations_for_user(db, user_id)

@router.get("/conversations/{conversation_id}/messages", response_model=list[message_schema.MessageOut])
@limiter.limit("60/minute")
def get_messages(request: Request, conversation_id: int, skip: int = 0, limit: int = 50, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return message_service.get_messages_in_conversation(db, conversation_id, user_id, skip, limit)

@router.post("/conversations/{conversation_id}/read")
@limiter.limit("60/minute")
def mark_read(request: Request, conversation_id: int, user_id: int = Depends(get_current_user_id), db: Session = Depends(get_db)):
    return message_service.mark_messages_as_read(db, conversation_id, user_id)


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
            
            if data.get("type") == "typing" and "conversation_id" in data:
                conversation_id = int(data["conversation_id"])
                is_typing = data.get("is_typing", False)
                
                conv_model = db.query(message_service.message_repository.Conversation).filter(
                    message_service.message_repository.Conversation.id == conversation_id
                ).first()
                
                if conv_model:
                    recipient_id = conv_model.user2_id if conv_model.user1_id == user_id else conv_model.user1_id
                    typing_event = {
                        "type": "typing",
                        "conversation_id": conversation_id,
                        "sender_id": user_id,
                        "is_typing": is_typing
                    }
                    await manager.send_personal_message(typing_event, recipient_id)
                continue

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
                    ).model_dump(mode="json")
                    
                    msg_out["type"] = "message"
                    
                    await manager.send_personal_message(msg_out, user_id)
                    await manager.send_personal_message(msg_out, recipient_id)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(user_id)
