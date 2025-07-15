import shutil
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.database import get_db
from app.main import app


# Setup a temporary database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Override the get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply the override
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {"message": "Hello World"}

def test_auth_code_flow(setup_database):
    email = "test@example.com"
    device_id = "device-123"

    # request OTP
    resp = client.post("/auth/code/request", json={"email": email, "device_id": device_id})
    assert resp.status_code == 200
    code = resp.json()["code"]
    assert len(code) == 6

    # verify OTP
    resp2 = client.post("/auth/code/verify", json={"code": code, "device_id": device_id})
    assert resp2.status_code == 200
    assert "session_token" in resp2.json()
    return resp2.json()["session_token"]

def test_file_upload_download(setup_database):
    session_token = test_auth_code_flow(setup_database)

    test_file_content = b"Hello, file!"
    file_name = "hello.txt"
    test_dir = "data"
    shutil.rmtree(test_dir, ignore_errors=True)

    headers = {"Authorization": f"Bearer {session_token}"}

    # Upload
    files = {
        "in_file": ("hello.txt", test_file_content, "text/plain"),
    }
    upload_resp = client.post("/file/upload/", files=files, headers=headers)
    print(upload_resp.content)
    assert upload_resp.status_code == 200
    upload_data = upload_resp.json()
    file_id = upload_data["file_id"]

    # List
    list_resp = client.get("/file/list/", headers=headers)
    print(f"List response status: {list_resp}")
    print(f"List response content: {list_resp.text}")
    assert list_resp.status_code == 200
    assert any(f["id"] == file_id for f in list_resp.json()["owned_files"])

    # Download
    download_resp = client.get(
        "/file/download/", 
        params={"file_id": file_id},
        headers=headers
    )
    assert download_resp.status_code == 200
    assert download_resp.content == test_file_content

    delete_resp = client.delete("/file/delete/", 
            params={"file_id": file_id},
            headers=headers
            )
    assert delete_resp.status_code == 200

    download_resp = client.get("/file/download/", 
    params={"file_id": file_id}, 
    headers=headers
    )
    assert download_resp.status_code == 403
