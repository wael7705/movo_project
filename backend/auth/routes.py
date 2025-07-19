from fastapi import APIRouter, Depends, Request, Body
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTStrategy, AuthenticationBackend, BearerTransport
from fastapi_users.manager import BaseUserManager
from fastapi_users.exceptions import UserAlreadyExists
from fastapi_users.router import get_auth_router, get_register_router
from backend.models.user import User, UserRole
from backend.auth.schemas import UserRead, UserCreate
from backend.auth.db import get_user_db
from backend.auth.config import SECRET, JWT_LIFETIME_SECONDS
from backend.auth.utils import hash_password
from fastapi_users.password import PasswordHelper
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.database import get_db
import random
import string
from typing import Dict
from datetime import datetime, timedelta

# Bearer transport for JWT
bearer_transport = BearerTransport(tokenUrl="/auth/login_by_phone/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=JWT_LIFETIME_SECONDS, token_audience=["fastapi-users:auth"])

# Authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

class UserManager(BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Request | None = None):
        pass

    async def create(self, user_create: UserCreate, safe: bool = False, request: Request | None = None) -> User:
        existing = await self.user_db.get_by_email(user_create.email) if user_create.email else None
        if existing:
            raise UserAlreadyExists
        user_dict = user_create.dict()
        user_dict["password"] = hash_password(user_create.password)
        user = await self.user_db.create(user_dict)
        return user

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

router = APIRouter()

# استخدم فقط المعاملات المطلوبة حسب التوثيق الرسمي
router.include_router(
    get_register_router(get_user_manager, UserRead, UserCreate),
    prefix="/auth/register_by_phone",
    tags=["auth"]
)

router.include_router(
    get_auth_router(auth_backend, get_user_manager, UserRead),
    prefix="/auth/login_by_phone",
    tags=["auth"]
)

# ذاكرة مؤقتة للـ OTP
otp_store: Dict[str, Dict[str, any]] = {}
OTP_EXPIRY_MINUTES = 5

@router.post("/auth/send_otp", tags=["auth"])
async def send_otp(phone: str = Body(..., embed=True)):
    otp = ''.join(random.choices(string.digits, k=6))
    otp_store[phone] = {"otp": otp, "expires": datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)}
    print(f"[OTP] Sent to {phone}: {otp}")
    return {"detail": "OTP sent successfully (check console in dev mode)", "expires_in": OTP_EXPIRY_MINUTES*60}

@router.post("/auth/verify_otp", tags=["auth"])
async def verify_otp(phone: str = Body(..., embed=True), otp: str = Body(..., embed=True)):
    record = otp_store.get(phone)
    if not record:
        return {"success": False, "detail": "No OTP sent to this phone."}
    if record["expires"] < datetime.utcnow():
        del otp_store[phone]
        return {"success": False, "detail": "OTP expired."}
    if record["otp"] != otp:
        return {"success": False, "detail": "Invalid OTP."}
    del otp_store[phone]
    return {"success": True, "detail": "OTP verified successfully."}

@router.get("/auth/me", response_model=UserRead, tags=["auth"])
async def get_me(user: User = Depends(fastapi_users.current_user(active=True))):
    return user 