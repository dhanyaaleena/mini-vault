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

**Components:**
- **Web/CLI Client:** User interacts via browser, CLI, or API client.
- **FastAPI App:** Handles authentication, session management, file encryption, business logic, and API endpoints.
- **PostgreSQL (DB):** Stores user info, session tokens, file metadata.
- **Encrypted Files (data/):** All uploaded files are encrypted and stored on disk.

**Flow:**
1. Client sends requests (register, upload, download, etc.) to FastAPI.
2. FastAPI authenticates, processes, and interacts with the database and file storage.
3. Files are encrypted before saving and decrypted on download.

## Backend Features in detail

- **FastAPI-based REST API:**
  - All endpoints are built using FastAPI for high performance and automatic OpenAPI docs.

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

## API Endpoints

### Authentication

| Method | Path                   | Description                                 | Auth Required |
|--------|------------------------|---------------------------------------------|--------------|
| POST   | /auth/code/request     | Request OTP for email/device                | No           |
| POST   | /auth/code/verify      | Verify OTP and get session token            | No           |
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

### **Authentication**
- All endpoints (except `/auth/code/request` and `/auth/code/verify`) require the `Authorization: Bearer <session_token>` header.
- Obtain a session token by verifying OTP.

### **File Upload Example (cURL)**
```bash
curl -X POST http://localhost:8000/file/upload/ \
  -H "Authorization: Bearer <session_token>" \
  -F "in_file=@/path/to/yourfile.txt"
```

### **File Download Example (cURL)**
```bash
curl -X GET "http://localhost:8000/file/download/?file_id=<file_id>" \
  -H "Authorization: Bearer <session_token>" --output yourfile.txt
```

---
