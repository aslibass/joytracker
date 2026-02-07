from fastapi_sso.sso.google import GoogleSSO
from database import settings
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session
import models

google_sso = GoogleSSO(
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    scope=["openid", "email", "profile"],
    allow_insecure_http=True # Set to False in production
)

async def get_or_create_user(db: Session, user_info: dict) -> models.User:
    user = db.query(models.User).filter(models.User.google_sub == user_info["id"]).first()
    if not user:
        user = models.User(
            email=user_info["email"],
            google_sub=user_info["id"],
            avatar_url=user_info.get("picture"),
            is_admin=False # Default
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
