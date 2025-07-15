# Mini Vault

A secure file vault web application built with FastAPI, SQLAlchemy, and PostgreSQL. Supports user authentication, encrypted file upload/download, sharing, and storage quota management.


## Features
- User registration and authentication (email/device + OTP)
- Secure session management with Bearer tokens
- Encrypted file upload, download, and sharing
- Premium and non-premium user storage quotas
- PostgreSQL database with SQLAlchemy ORM
- Dockerized for easy deployment

---

## Architecture Overview

```mermaid
graph TD
    subgraph Client
        A[Web/CLI Client]
    end
    subgraph API
        B[FastAPI App]
        C[Session & Auth]
        D[File Encryption]
        E[CRUD Logic]
    end
    subgraph Storage
        F[PostgreSQL DB]
        G[Encrypted Files (data/)]
    end
    A -- HTTP/HTTPS --> B
    B -- DB ORM --> F
    B -- File I/O --> G
    B -- Session/Token Mgmt --> C
    B -- Encryption --> D
    B -- Business Logic --> E
```

- **FastAPI App**: Handles all HTTP requests, authentication, and business logic
- **Session & Auth**: Issues and validates secure session tokens (Bearer)
- **File Encryption**: Encrypts files before storing on disk
- **CRUD Logic**: Handles database operations
- **PostgreSQL**: Stores user, session, and file metadata
- **data/**: Stores encrypted file blobs

---

## Deployment (Docker)

### **Requirements**
- Docker & Docker Compose
- (Optional) Python 3.12+ for local development

### **Quick Start**

1. **Clone the repository**
    ```bash
    git clone <your-repo-url>
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

## Security Notes
- All file data is encrypted at rest using Fernet symmetric encryption
- Session tokens are cryptographically secure and passed via Authorization header
- Non-premium users are limited to 5GB total storage
- Premium users have unlimited storage

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
