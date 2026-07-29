from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.chat import ChatSession


async def create_session(session_name: str, user_id: int, db: AsyncSession) -> ChatSession:
    if not session_name or not user_id:
        raise HTTPException(status_code=400, detail="Session name and user ID are required")

    session_name = session_name.strip()
    if len(session_name) < 1:
        raise HTTPException(status_code=400, detail="Session name cannot be empty")

    try:
        new_session = ChatSession(session_name=session_name, user_id=user_id)
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        return new_session
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


async def get_user_sessions(user_id: int, db: AsyncSession) -> list[ChatSession]:
    try:
        result = await db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(ChatSession.created_at.desc())
        )
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sessions: {str(e)}")


async def get_session_by_id(session_id: int, user_id: int, db: AsyncSession) -> ChatSession:
    try:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id
            )
        )
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=404, detail="Session not found or access denied")

        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch session: {str(e)}")
