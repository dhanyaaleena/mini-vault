from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from datetime import datetime, timedelta, UTC
from uuid import uuid4
from app.models import User, AuthCode, SessionToken, File, SharedFile
from .exceptions import *
import os
import secrets


def get_user(email, db):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    return user

def create_user_and_otp(email:str, device_id:str, code:str, db: Session):
    user = get_user(email, db)

    if not user:
        user = User(email=email)
        db.add(user)
        db.flush()  # Get the user.id without commit

    # Create an OTP in the table
    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=10)  # OTP valid for 10 minutes

    auth_code = AuthCode(
        user_id=user.id,
        code=code,
        device_id=device_id,
        created_at=now,
        expires_at=expires_at
    )
    db.add(auth_code)
    db.commit()

def verify_code_and_generate_session(code:str, device_id:str, db: Session):
    login_code = (
        db.query(AuthCode)
        .filter(
            AuthCode.code == code,
            AuthCode.device_id == device_id,
            AuthCode.expires_at > datetime.now(UTC)
        )
        .first()
    )

    if not login_code:
        raise InvalidCode(details="Invalid or expired code")

    session_id = secrets.token_urlsafe(32)
    session_data = {
        "user_id": str(login_code.user_id),
        "device_id": device_id
    }
    expires_at = datetime.now(UTC) + timedelta(minutes=60)

    new_session = SessionToken(
        session_id=str(session_id),
        data=session_data,
        expires_at=expires_at
    )

    db.add(new_session)

    # OTP can we used for validation only once
    db.execute(
        delete(AuthCode).where(
            AuthCode.code == code,
            AuthCode.device_id == device_id
        )
    )

    db.commit()

    return session_id

def check_and_get_session_details(session_id: str, db: Session):
    session = db.query(SessionToken).filter(
        SessionToken.session_id == session_id,
        SessionToken.expires_at > datetime.now(UTC)
    ).first()
    if not session:
        raise InvalidSession("Invalid or expired session")
    return session

def create_file_entry(location:str, file_name:str, file_id: str, db:Session, checksum:str, file_size: str, user: User):
    new_file = File(
        id=str(file_id),
        location=location,
        owner_user_id=user.id,
        checksum=checksum,
        file_name=file_name,
    )
    user.current_storage = (user.current_storage or 0) + file_size
    db.add(new_file)
    db.commit()

def get_file_location_as_owner(owner_id:str, file_id:str, db:Session):
    file = db.query(File).filter(
        File.id == file_id,
        File.owner_user_id ==owner_id
    ).first()
    if not file:
        raise FileNotFound(details="File not found")
    return file.location, file.file_name

def add_share_file(file_id, email, db):
    user = get_user(email, db)
    if not user:
        raise UserNotFound(details="User not found")
    shared = SharedFile(file_id = file_id, shared_user_id = user.id)
    db.add(shared)
    db.commit()

def is_owner(file_id, user_id, db) -> bool:
    file = db.query(File).filter(File.owner_user_id == user_id, File.id == file_id).first()
    if not file:
        return False
    return True

def list_owned_files(owner_id: str, db: Session):
    files = db.query(File).filter(File.owner_user_id ==owner_id).all()
    files_list = []
    for file in files:  
        file_info = {
            "id": str(file.id),
            "created_at": file.created_at.isoformat(),
            "file_name": file.file_name
        }
        files_list.append(file_info)

    return files_list

def list_shared_files(shared_user_id: str, db: Session):
    shared_entries = db.query(SharedFile).filter(SharedFile.shared_user_id == shared_user_id).all()
    shared_files = []
    for entry in shared_entries:
        file = db.query(File).filter(File.id == entry.file_id).first()
        if file:
            owner = db.query(User).filter(User.id == file.owner_user_id).first()
            shared_files.append({
                "id": file.id,
                "created_at": file.created_at.isoformat(),
                "file_name": file.file_name,
                "owner_user_id" : owner.id,
                "shared_at": entry.shared_at.isoformat()
            })
    return shared_files

def delete_session(session, db):
    db.delete(session)
    db.commit()

def delete_file_from_storage(file_id: str, user_id: str, db: Session):
    file = db.query(File).filter(File.id == file_id, File.owner_user_id == user_id).first()
    if not file:
        raise FileNotFound("File not found or you do not have permission to delete it.")
    file_size = os.path.getsize(file.location)
    user = db.query(User).filter(User.id == user_id).first()
    user.current_storage = max(0, user.current_storage - file_size)
    file_path = file.location
    db.delete(file)
    db.commit()
    return file_path

def upgrade_user_plan(user_id:str, db:Session):
    user = db.query(User).filter(User.id == user_id).first()
    user.is_paid = True
    db.commit()