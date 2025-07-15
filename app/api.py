from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Query
from app.database import get_db
from app.schema import CodeRequest, VerifyCodeRequest, ShareFileRequest
from .crud import *
import hashlib
from io import BytesIO
from fastapi import Depends, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session
import random
import string
import os
from uuid import uuid4, UUID
from . import models
from .database import engine, get_db
from .crud import *
from .exceptions import *
from dotenv import load_dotenv


router = APIRouter()
security = HTTPBearer()

load_dotenv()
models.Base.metadata.create_all(bind=engine)

fernet = Fernet(os.environ["FILE_ENCRYPTION_KEY"])
storage_location = os.environ["STORAGE_LOCATION"]

def generate_otp_letters():
    return ''.join(random.choices(string.ascii_letters, k=6))
    
def check_valid_file_uuid(uuid_string: str) -> bool:
    try:
        UUID(uuid_string)
    except ValueError:
         raise FileNotFound("invalid file id")
    
def get_user_id_from_session(session_id: str, db:Session) -> str:
    session_data = check_and_get_session_details(session_id, db).data

    user_id = session_data.get("user_id")
    if user_id is None:
        return UserNotFound("Invalid user")
    return session_data


@router.get("/")
def root():
    return {"message": "Hello World"}

@router.post("/auth/code/request")
def getCode(code_request: CodeRequest, db: Session = Depends(get_db)):
    code = generate_otp_letters()
    create_user_and_otp(code_request.email, code_request.device_id, code, db)

    return {"code":code}

@router.post("/auth/code/verify")
def verifyCode(verify_code_request: VerifyCodeRequest, db: Session = Depends(get_db)):
    code = verify_code_request.code
    device_id = verify_code_request.device_id

    return {"session_token":verify_code_and_generate_session(code, device_id, db)}
    
@router.post("/file/upload/")
def uploadFile(
        in_file: UploadFile, 
        token: str = Depends(security),
        db: Session = Depends(get_db)
    ):
    session_id = token.credentials
    user_id = get_user_id_from_session(session_id, db).get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    contents = in_file.file.read()
    file_size = len(contents)
    if not user.is_paid:
        current_storage = user.current_storage or 0
        if current_storage + file_size > 5 * 1024 * 1024 * 1024:  # 5 GB
            raise HTTPException(status_code=403, detail="Free storage limit (5GB) exceeded.")
    
    file_id = uuid4()
    os.makedirs(storage_location, exist_ok=True)
    out_file_path = os.path.join(storage_location, f"{file_id}_{in_file.filename}")
    hash_sha256 = hashlib.sha256()
    hash_sha256.update(contents)
    encrypted_contents = fernet.encrypt(contents)
    with open(out_file_path, 'wb') as out_file:
        out_file.write(encrypted_contents)

    create_file_entry(
        db=db,
        file_id=file_id,
        location=out_file_path,
        checksum=hash_sha256.hexdigest(),
        file_name = in_file.filename,
        file_size=file_size,
        user=user
    )
    return {"file_id": str(file_id), "checksum": hash_sha256.hexdigest()}

    
@router.get("/file/download/")
def downloadFile(
        file_id: str = Query(),
        token: str = Depends(security),
        db: Session = Depends(get_db)
    ):
    session_id = token.credentials     
    check_valid_file_uuid(file_id)
    
    user_id = check_and_get_session_details(session_id, db).data.get("user_id")
    file_location, file_name = get_file_location_as_owner(owner_id= user_id, file_id=file_id, db=db)
    with open(file_location, 'rb') as f:
        encrypted_data = f.read()
    decrypted_data = fernet.decrypt(encrypted_data)

    return StreamingResponse(
        BytesIO(decrypted_data),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )

@router.post("/file/share/", tags=["files"])
def share_file(
    request: ShareFileRequest, 
    token: str = Depends(security),
    db: Session = Depends(get_db)
    ):
    session_id = token.credentials
    user_id = get_user_id_from_session(session_id, db).get("user_id")
    if not is_owner(file_id=request.file_id, user_id=user_id, db=db):
        raise FilePermissionError(details= "File not accessible")
    add_share_file(request.file_id, request.email, db)
    return {"status" : "ok"}

@router.get("/file/list/")
def listFiles(
        token: str = Depends(security),
        db: Session=Depends(get_db)
    ):
    session_id = token.credentials
    user_id = get_user_id_from_session(session_id, db).get("user_id")
    owned_files = list_owned_files(owner_id=user_id, db=db)
    shared_files = list_shared_files(shared_user_id = user_id, db=db)
    return {
        "owned_files": owned_files,
        "shared_files": shared_files
    }

@router.delete("/file/delete/")
def delete_file(
    file_id: str = Query(),
    token: str = Depends(security),
    db: Session = Depends(get_db)
):
    session_id = token.credentials
    check_valid_file_uuid(file_id)
    session_data = check_and_get_session_details(session_id, db).data
    user_id = session_data.get("user_id")
    file_path = delete_file_from_storage(file_id, user_id, db)
    if os.path.exists(file_path):
        os.remove(file_path)
    return {
        "status": "ok"
    }

@router.post("/auth/logout/")
def logout(
    token: str = Depends(security), 
    db: Session=Depends(get_db)
    ):
    session_id = token.credentials
    session = check_and_get_session_details(session_id, db)
    delete_session(session, db)
    return {
        "status" : "ok"
    }

@router.get("/user/storage/")
def get_user_storage(
        token: str = Depends(security),
        db = Depends(get_db)
    ):
    session_id = token.credentials
    user_id = get_user_id_from_session(session_id, db).get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    return {
        "current_storage_bytes" : user.current_storage,
        "is_paid" : user.is_paid
    }

@router.post("/user/upgrade/")
def upgrade_user(
        token: str = Depends(security),
        db = Depends(get_db)
    ):
    session_id = token.credentials
    user_id = get_user_id_from_session(session_id, db).get("user_id")
    #Do payment here
    upgrade_user_plan(user_id, db)
    return {
        "status" : "ok"
    }

    # verify if the otp and device_id exitst in the table
    # create session code
    # create entry in table, with user_email
    # return session code
    
    # return {"session_token":session_token}

