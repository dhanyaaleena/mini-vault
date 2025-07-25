# Mini Vault

A secure file vault web application built with FastAPI, SQLAlchemy, and PostgreSQL. Supports user authentication, encrypted file upload/download, sharing, and storage quota management.

## Architecture Overview

```
[ Web/CLI Client ]
         |
         v
   [ FastAPI App ]
     /         \
    v           v
[PostgreSQL] [Encrypted Files]
   (DB)         (data/)
```

**Flow:**
1. Client sends requests (register, upload, download, etc.) to FastAPI.
2. FastAPI authenticates, processes, and interacts with the database and file storage.
3. Files are encrypted before saving and decrypted on download.

## Backend Features in detail

- **FastAPI-based REST API:**
  - All endpoints are built using FastAPI.

- **User Authentication & Session Management:**
  - Users authenticate via email/device and OTP (one-time password).
  - Secure session tokens are generated using cryptographically secure random values.
  - Session tokens are passed via the `Authorization: Bearer <token>` header for all protected endpoints.
  - Sessions have expiration and can be invalidated on logout.

- **Role & Plan Management:**
  - Users are categorized as premium or non-premium.
  - Non-premium users have a 5GB total storage quota; premium users have unlimited storage.
  - Storage usage is tracked and enforced at upload time.

- **Encrypted File Storage:**
  - All uploaded files are encrypted at rest using Fernet symmetric encryption.
  - Files are stored on disk in the `data/` directory, never in plaintext.
  - Files are decrypted on-the-fly when downloaded by authorized users.

- **File Sharing:**
  - Users can share files with other registered users by email.
  - Shared files are listed separately from owned files.

- **Database & Models:**
  - Uses SQLAlchemy ORM for all database operations.
  - PostgreSQL is used in the app; SQLite is used for testing.
  - Alembic is used for database migrations.

- **Custom Error Handling:**
  - All errors are returned as JSON with appropriate HTTP status codes.
  - Custom exception handlers for authentication, authorization, and file errors.

- **Testing Support:**
  - Pytest-based test suite with a temporary SQLite database.
  - Test coverage for authentication, file upload/download, and sharing.

- **Dockerized Deployment:**
  - All services (API, DB) are containerized for easy local and production deployment.
  - One-command startup with `run_app.sh`.

---

## Deployment (Docker)

### **Requirements**
- Docker & Docker Compose

### **Quick Start**

1. **Clone the repository**
    ```bash
    git clone https://github.com/dhanyaaleena/mini-vault.git
    cd mini-vault
    ```

2. **(Optional) Set your encryption key**
    - By default, the key is hardcoded in `docker-compose.yml` as `FILE_ENCRYPTION_KEY`.
    - For better security, generate your own key:
      ```python
      from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())
      ```
    - Update the value in `docker-compose.yml`.

3. **Run the application**
    ```bash
    chmod +x run_app.sh
    ./run_app.sh
    ```

4. **Access the API**
    - Main API: http://localhost:8000
    - Swagger Docs: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc

---

## Configuration
- All configuration is via environment variables (see `docker-compose.yml`)
- Uploaded files are stored in `data/` (mounted as a Docker volume)
- Database data is persisted in a Docker volume (`postgres_data`)

---

## Testing
- Tests use a temporary SQLite database
- To run tests locally:
    ```bash
    pytest tests/
    ```
---

## Project Structure
```
mini-vault/
├── app/
│   ├── api.py           # API endpoints
│   ├── main.py          # FastAPI app instance
│   ├── crud.py          # Database logic
│   ├── models.py        # SQLAlchemy models
│   ├── schema.py        # Pydantic schemas
│   ├── error_handlers.py# Custom error handlers
│   └── ...
├── data/                # Encrypted file storage (Docker volume)
├── tests/               # Test suite
├── Dockerfile           # Docker build file
├── docker-compose.yml   # Docker Compose config
├── requirements.txt     # Python dependencies
├── run_app.sh           # App runner script
└── README.md            # This file
```

---

## How to Test the API

You can test the Mini Vault API using tools like **curl**, **Postman**, **Swagger** or any HTTP client. For testing the download paste the url in browser.
Here’s how to use the example requests below:

### 1. Register & Authenticate
- Start by requesting an OTP with your email and device ID.
- Use the OTP to verify and receive a session token.
- **Note:** The session token must be included as a Bearer token in the `Authorization` header for all protected endpoints.

### 2. Upload, List, Download, Share, and Manage Files
- Use the session token in the `Authorization` header for all file and user endpoints.
- For file upload, use a multipart/form-data request (see curl example).
- For file download, use the file ID returned from upload or list.
- To share a file, provide the file ID and the recipient's email.
- To check your storage or upgrade, use the respective endpoints with your session token.

### 3. Example Workflow
1. **Request OTP:**
    - `POST /auth/code/request/` with your email and device ID.
2. **Verify OTP:**
    - `POST /auth/code/verify/` with the code and device ID. Save the `session_token` from the response.
3. **Upload a File:**
    - Use the `session_token` in the `Authorization` header and upload a file.
4. **List Files:**
    - Use the same `session_token` to list your files.
5. **Download a File:**
    - Use the file ID from the list/upload response and your `session_token`.
6. **Share a File:**
    - Use the file ID and the recipient's email, with your `session_token`.
7. **Check Storage or Upgrade:**
    - Use the `/user/storage/` and `/user/upgrade/` endpoints with your `session_token`.
8. **Logout:**
    - Call `/auth/logout/` with your `session_token` to invalidate your session.

### 4. Tips
- If you get a 401/403 error, check that your session token is valid and not expired.
- Always use the `Authorization: Bearer <session-token>` header for protected endpoints.
- Use the Swagger UI at `http://localhost:8000/docs` for interactive API testing and to see all request/response schemas.
- For file upload in Postman, use the "form-data" body type and set the key to `in_file`.

---


## API  Details

Below are the API details for using the Mini Vault API, with example requests and responses.

### 1. Request OTP (Registration/Login)
**Request:**
```http
POST /auth/code/request/
Content-Type: application/json

{
  "email": "user@example.com",
  "device_id": "device-123"
}
```
**Response:**
```json
{
  "code": "ABCDEF"
}
```

### 2. Verify OTP and Get Session Token
**Request:**
```http
POST /auth/code/verify/
Content-Type: application/json

{
  "code": "ABCDEF",
  "device_id": "device-123"
}
```
**Response:**
```json
{
  "session_token": "<your-session-token>"
}
```

### 3. Upload a File
**Request:**
```bash
curl -X POST http://localhost:8000/file/upload/ \
  -H "Authorization: Bearer <session-token>" \
  -F "in_file=@/path/to/yourfile.txt"
```
**Response:**
```json
{
  "file_id": "<file-id>",
  "checksum": "..."
}
```

### 4. List Files
**Request:**
```http
GET /file/list/
Authorization: Bearer <session-token>
```
**Response:**
```json
{
  "owned_files": [
    {"id": "<file-id>", "created_at": "2024-07-15T12:00:00Z", "file_name": "yourfile.txt"}
  ],
  "shared_files": []
}
```

### 5. Download a File
**Request:**
```bash
curl -X GET "http://localhost:8000/file/download/?file_id=<file-id>" \
  -H "Authorization: Bearer <session-token>" --output yourfile.txt
```

### 6. Logout
**Request:**
```http
POST /auth/logout/
Authorization: Bearer <session-token>
```
**Response:**
```json
{
  "detail": "ok"
}
```

### 7. Share a File
**Request:**
```http
POST /file/share/
Authorization: Bearer <session-token>
Content-Type: application/json

{
  "file_id": "<file-id>",
  "email": "otheruser@example.com"
}
```
**Response:**
```json
{
  "status": "ok"
}
```

### 8. Get User Storage Info
**Request:**
```http
GET /user/storage/
Authorization: Bearer <session-token>
```
**Response:**
```json
{
  "current_storage_bytes": 123456,
  "is_paid": false
}
```

### 9. Upgrade User to Premium
**Request:**
```http
POST /user/upgrade/
Authorization: Bearer <session-token>
```
**Response:**
```json
{
  "detail": "ok"
}
```

---

## API Endpoints Summary

### Authentication

| Method | Path                   | Description                                 | Auth Required |
|--------|------------------------|---------------------------------------------|--------------|
| POST   | /auth/code/request/    | Request OTP for email/device                | No           |
| POST   | /auth/code/verify/     | Verify OTP and get session token            | No           |
| POST   | /auth/logout/          | Logout and invalidate session               | Yes          |

### File Operations

| Method | Path                   | Description                                 | Auth Required |
|--------|------------------------|---------------------------------------------|--------------|
| POST   | /file/upload/          | Upload a file (encrypted at rest)           | Yes          |
| GET    | /file/download/        | Download a file (decrypted on the fly)      | Yes          |
| GET    | /file/list/            | List owned and shared files                 | Yes          |
| POST   | /file/share/           | Share a file with another user              | Yes          |
| DELETE | /file/delete/          | Delete a file you own                       | Yes          |

### User & Plan

| Method | Path                   | Description                                 | Auth Required |
|--------|------------------------|---------------------------------------------|--------------|
| GET    | /user/storage/         | Get current storage usage and plan info     | Yes          |
| POST   | /user/upgrade/         | Upgrade to premium plan                     | Yes          |

---
