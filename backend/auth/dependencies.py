from fastapi import Depends, HTTPException, status
from backend.models.user import UserRole
# استيراد fastapi_users بعد التهيئة الصحيحة
from backend.auth.routes import fastapi_users
from backend.models.user import User

async def role_required(role: str):
    def dependency(user: User = Depends(fastapi_users.current_user(active=True))):
        # حماية إضافية ضد ColumnElement أو أنواع غير متوقعة
        user_role = user.role
        if hasattr(user_role, 'name'):
            user_role = user_role.name
        if not isinstance(user_role, str):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User role is not a string or enum."
            )
        if user_role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    return dependency 