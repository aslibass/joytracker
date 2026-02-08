from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    google_client_id: str
    google_client_secret: str
    gemini_api_key: str
    smtp_login: str = ""
    smtp_password: str = ""
    leader_emails: str = ""
    leader_phones: str = ""
    enable_sms: bool = False
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_number: str = ""
    secret_key: str = "super-secret-key"
    port: int = 8000

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
