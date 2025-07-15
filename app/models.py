from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, BigInteger
from app.database import Base
from datetime import datetime, UTC
from uuid import uuid4

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, index=True)
    is_paid = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    current_storage = Column(BigInteger, default=0)


class AuthCode(Base):
    __tablename__ = "auth_codes"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    code = Column(String(6), nullable=False)
    device_id = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    expires_at = Column(DateTime)


class SessionToken(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    data = Column(JSON, nullable=False)
    session_id = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    expires_at = Column(DateTime, nullable=False)


class File(Base):
    __tablename__ = "files"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    checksum = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    owner_user_id = Column(String, ForeignKey("users.id"))
    location = Column(String, nullable=False)
    file_name = Column(String, nullable=False)


class SharedFile(Base):
    __tablename__ = "shared_files"
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    file_id = Column(String, ForeignKey("files.id"))
    shared_user_id = Column(String, ForeignKey("users.id"))
    shared_at = Column(DateTime, default=lambda: datetime.now(UTC))
    permission = Column(String, default="read")
