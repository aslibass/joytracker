from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from database import settings
from fastapi import HTTPException
from sqlalchemy.orm import Session
import models

# We no longer need the legacy GoogleSSO object for the modern GIS flow
# google_sso = ... (removed)

def verify_google_id_token(token: str) -> dict:
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), settings.google_client_id)
        return idinfo
    except ValueError:
        # Invalid token
        raise HTTPException(status_code=401, detail="Invalid Google ID Token")

async def get_or_create_user(db: Session, user_info: dict) -> models.User:
    google_id = user_info.get("sub")
    email = user_info.get("email")
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
