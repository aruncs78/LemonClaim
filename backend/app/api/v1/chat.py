"""AI Chat API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.models.chat_history import ChatHistory, ChatRole
from app.models.policy import Policy
from app.models.claim import Claim
from app.schemas.chat import ChatRequest, ChatResponse, ChatFeedback
from typing import List
from datetime import datetime
import uuid

router = APIRouter()

DEMO_RESPONSES = {
    "greeting": ["Hi there! 👋 I'm Maya, your insurance assistant. How can I help you today?"],
    "quote": ["I'd love to help you get a quote! What type of insurance are you looking for?"],
    "claim": ["I'm sorry to hear you need to file a claim. Let me help you. What happened?"],
    "status": ["I can check that for you! Looking at your claims now..."],
    "help": ["I can help with: quotes, claims, policies, and payments. What would you like?"],
    "thanks": ["You're welcome! Anything else I can help with?"],
    "default": ["I understand. Could you tell me more about what you're looking for?"]
}

def detect_intent(message: str) -> str:
    message_lower = message.lower()
    if any(g in message_lower for g in ["hi", "hello", "hey"]): return "greeting"
    if any(w in message_lower for w in ["quote", "price", "cost"]): return "quote"
    if any(w in message_lower for w in ["claim", "file", "accident"]): return "claim"
    if any(w in message_lower for w in ["status", "update", "track"]): return "status"
    if any(w in message_lower for w in ["help", "options"]): return "help"
    if any(w in message_lower for w in ["thank", "thanks"]): return "thanks"
    return "default"

@router.post("/message", response_model=ChatResponse)
async def send_message(chat_request: ChatRequest, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    session_id = chat_request.session_id or str(uuid.uuid4())
    intent = detect_intent(chat_request.message)
    response_message = DEMO_RESPONSES.get(intent, DEMO_RESPONSES["default"])[0]
    
    if intent == "status":
        claims_result = await db.execute(select(Claim).where(Claim.user_id == user_id, Claim.is_deleted == False).order_by(Claim.created_at.desc()).limit(3))
        claims = claims_result.scalars().all()
        if claims:
            response_message += "\n\nYour recent claims:\n"
            for claim in claims:
                response_message += f"\n• {claim.claim_number}: {claim.status.value.replace('_', ' ').title()}"
        else:
            response_message = "You don't have any claims on file."
    
    user_chat = ChatHistory(user_id=user_id, session_id=session_id, role=ChatRole.USER, message=chat_request.message, intent=intent)
    assistant_chat = ChatHistory(user_id=user_id, session_id=session_id, role=ChatRole.ASSISTANT, message=response_message, intent=intent)
    db.add(user_chat)
    db.add(assistant_chat)
    await db.commit()
    
    return ChatResponse(message=response_message, session_id=session_id, intent=intent, requires_action=False, suggestions=["Get a quote", "File a claim", "Check status"])

@router.get("/history", response_model=List[dict])
async def get_chat_history(session_id: str = None, limit: int = 50, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    query = select(ChatHistory).where(ChatHistory.user_id == user_id)
    if session_id: query = query.where(ChatHistory.session_id == session_id)
    query = query.order_by(ChatHistory.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return [m.to_dict() for m in reversed(result.scalars().all())]

@router.delete("/history", response_model=dict)
async def clear_chat_history(session_id: str = None, user_id: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    query = select(ChatHistory).where(ChatHistory.user_id == user_id)
    if session_id: query = query.where(ChatHistory.session_id == session_id)
    result = await db.execute(query)
    for message in result.scalars().all(): await db.delete(message)
    await db.commit()
    return {"success": True, "message": "Chat history cleared"}
