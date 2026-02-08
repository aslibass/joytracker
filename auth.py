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

async def get_or_create_user(db: Session, user_info: any) -> models.User:
    # Handle both OpenID object and dict for flexibility
    if hasattr(user_info, "id"):
        google_id = user_info.id
        email = user_info.email
        picture = user_info.picture
    else:
        google_id = user_info["id"]
        email = user_info["email"]
        picture = user_info.get("picture")

    user = db.query(models.User).filter(models.User.google_sub == google_id).first()
    if not user:
        user = models.User(
            email=email,
            google_sub=google_id,
            avatar_url=picture,
            is_admin=False # Default
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
