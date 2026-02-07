from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    google_sub = Column(String, unique=True, index=True)
    avatar_url = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    entries = relationship("JoyEntry", back_populates="owner")

class JoyEntry(Base):
    __tablename__ = "joy_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # AI Classification Fields
    category = Column(String, nullable=True) # Faith, Family, Provision, Health, Nature, Work, Other
    tags = Column(JSON, default=[])
    sentiment_score = Column(Integer, nullable=True) # 1-10
    is_urgent = Column(Boolean, default=False)
    pastor_summary = Column(Text, nullable=True)

    owner = relationship("User", back_populates="entries")
