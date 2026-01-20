from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.features.auth.models import User
from app.features.auth import schemas
from app.core.config import get_settings

import logging
router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=dict)
async def register_user(
    user_in: schemas.UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    background_tasks: BackgroundTasks
):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalar_one_or_none()
    
    import random
    import string
    from datetime import datetime, timezone
    from app.core.email import send_otp_email

    otp = ''.join(random.choices(string.digits, k=6))
    otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)

    if existing_user:
        if existing_user.is_active:
            raise HTTPException(
                status_code=400,
                detail="User with this email already exists"
            )
        else:
            # Resend OTP
            existing_user.hashed_password = get_password_hash(user_in.password) # Update password just in case
            existing_user.verification_code = otp
            existing_user.verification_code_expires_at = otp_expiry
            db.add(existing_user)
            await db.commit()
            
            # Send Email (Background task to avoid blocking)
            background_tasks.add_task(send_otp_email, user_in.email, otp)
            
            return {"message": "OTP sent to email", "email": user_in.email}
    
    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        is_active=False,
        verification_code=otp,
        verification_code_expires_at=otp_expiry
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    background_tasks.add_task(send_otp_email, user_in.email, otp)
    
    return {"message": "OTP sent to email", "email": user_in.email}

@router.post("/verify-otp", response_model=schemas.Token)
async def verify_otp(
    verification_data: schemas.VerifyOTP,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    from datetime import datetime, timezone
    
    result = await db.execute(select(User).where(User.email == verification_data.email))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
        
    if user.is_active:
        # Already verified, just login logic if needed, or error
        # Let's just create token
        pass
    else:
        # Check OTP
        if not user.verification_code or user.verification_code != verification_data.otp:
             raise HTTPException(status_code=400, detail="Invalid OTP")
             
        if user.verification_code_expires_at and datetime.now(timezone.utc) > user.verification_code_expires_at:
             raise HTTPException(status_code=400, detail="OTP expired")
             
        # Activate
        user.is_active = True
        user.verification_code = None
        user.verification_code_expires_at = None
        db.add(user)
        await db.commit()
        
    # Create Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Login failed for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User not verified. Please verify your email.")

    logger.info(f"User logged in successfully: {user.email}")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

from app.features.auth.deps import get_current_user

@router.post("/verify")
async def verify_user_password(
    data: schemas.PasswordVerification,
    current_user: Annotated[User, Depends(get_current_user)]
):
    if not verify_password(data.password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid password")
    return {"valid": True}
