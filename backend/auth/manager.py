from fastapi_users.manager import BaseUserManager
from fastapi_users.exceptions import UserAlreadyExists
from backend.models.user import User
from backend.auth.db import get_user_db
from backend.auth.config import SECRET
from backend.auth.schemas import UserCreate
from fastapi import Request, Depends

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
        user = await self.user_db.create(user_dict)
        return user

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db) 