"""Chat API router with SSE streaming - BE-003 / BE-009."""

import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.database import get_db
from app.modules.auth.models import User
from app.modules.chat.schemas import (
    ChatMessageCreate,
    ChatSessionDetail,
    ChatSessionResponse,
)
from app.modules.chat.service import ChatService

router = APIRouter(prefix="/api/v1/chat", tags=["AI 对话"])


@router.get("/sessions", response_model=list[ChatSessionResponse])
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all chat sessions for the current user."""
    service = ChatService(db)
    return await service.get_sessions(current_user.id)


@router.get("/sessions/{session_id}", response_model=ChatSessionDetail)
async def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a chat session with full message history."""
    service = ChatService(db)
    session = await service.get_session_detail(session_id, current_user.id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a chat session and all its messages."""
    service = ChatService(db)
    deleted = await service.delete_session(session_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted"}


@router.post("/message")
async def send_message(
    data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Send a chat message and receive AI response via SSE stream.

    If session_id is provided, appends to existing session.
    If omitted, creates a new session automatically.
    Returns a Server-Sent Events stream with real-time updates.
    """
    service = ChatService(db)

    # Resolve or create session
    if data.session_id:
        session = await service.get_session_detail(
            data.session_id, current_user.id
        )
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
        session_id = data.session_id
    else:
        session = await service.create_session(
            user_id=current_user.id, title=data.content[:50]
        )
        session_id = session.id

    # Save user message
    await service.add_message(
        session_id=session_id, role="user", content=data.content
    )
    await db.commit()

    # Stream AI response via SSE
    async def event_stream():
        """Generate SSE events for AI chat response."""
        try:
            # Import here to avoid circular dependency
            from app.modules.chat.ai_engine import AIEngine

            engine = AIEngine()
            async for event in engine.chat_stream(
                session_id=session_id,
                user_message=data.content,
                db=db,
            ):
                yield f"event: {event['type']}\ndata: {json.dumps(event, default=str)}\n\n"
        except Exception as exc:
            error_event = {
                "type": "error",
                "content": f"AI processing error: {exc!s}",
            }
            yield f"event: error\ndata: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
