from datetime import timedelta

SECRET = "CHANGE_ME_SUPER_SECRET_KEY"  # ضع هذا في env في الإنتاج
JWT_LIFETIME_SECONDS = 60 * 60 * 24 * 7  # أسبوع
JWT_ALGORITHM = "HS256"
 
fastapi_users_settings = {
    "secret": SECRET,
    "lifetime_seconds": JWT_LIFETIME_SECONDS,
    "algorithm": JWT_ALGORITHM,
} 