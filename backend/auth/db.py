from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from backend.models.user import User
from backend.database.database import get_db
from typing import AsyncGenerator

# دالة تهيئة قاعدة بيانات المستخدمين لـ fastapi-users مع حماية ضد الأخطاء
async def get_user_db(session: AsyncSession = Depends(get_db)) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    try:
        yield SQLAlchemyUserDatabase(session, User)
    except Exception as e:
        # سجل الخطأ أو أرسله إلى نظام مراقبة
        print(f"[get_user_db] Error initializing SQLAlchemyUserDatabase: {e}")
        raise e 