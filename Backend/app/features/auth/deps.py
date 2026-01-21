from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.features.auth.models import User
from app.core.database import get_db

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    # 1. OPTIONAL: Check if user is already attached (e.g. by some other middleware)
    if hasattr(request.state, "user") and request.state.user:
        return request.state.user

    # 2. Check for email claim from stateless middleware
    if not hasattr(request.state, "user_email") or not request.state.user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    # 3. Fetch User from DB
    result = await db.execute(select(User).where(User.email == request.state.user_email))
    user = result.scalar_one_or_none()
    
    if not user:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
        
    if not user.is_active:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    # Cache it on request state for subsequent calls in same request?
    request.state.user = user
    return user
