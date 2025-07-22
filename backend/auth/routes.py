from fastapi import APIRouter
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTStrategy, AuthenticationBackend, BearerTransport
from backend.models.user import User
from backend.auth.db import get_user_db
from backend.auth.schemas import UserRead, UserCreate
from backend.auth.config import SECRET, JWT_LIFETIME_SECONDS
from backend.auth.manager import get_user_manager  # يجب أن يكون لديك هذا الملف

bearer_transport = BearerTransport(tokenUrl="/api/v1/auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=JWT_LIFETIME_SECONDS)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

router = APIRouter()

# تسجيل مستخدم جديد
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
# تسجيل الدخول JWT
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
# إدارة المستخدمين (اختياري)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserCreate),
    prefix="/users",
    tags=["users"],
) 