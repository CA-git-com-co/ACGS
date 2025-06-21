# Auth Service

## Purpose

Handles user authentication with JWT tokens and role-based access control.

## Main Features

- User registration and login flows
- JWT access and refresh tokens
- CSRF protection and secure cookie handling

## Key API Endpoints

- `/register` - create a new user account
- `/token` or `/login` - obtain access and refresh tokens
- `/token/refresh` - refresh expired access tokens
- `/logout` - revoke current tokens
- `/me` - retrieve the authenticated user profile

## Setup

1. Install dependencies:

   ```bash
   # Using UV package manager (recommended)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source ~/.bashrc
   uv sync

   # Alternative: Traditional pip
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and set:
   - `DATABASE_URL` - PostgreSQL connection URL
   - `SECRET_KEY` and `ALGORITHM` for JWT signing
   - `ACCESS_TOKEN_EXPIRE_MINUTES` and `REFRESH_TOKEN_EXPIRE_DAYS`
   - `CSRF_SECRET_KEY` for CSRF tokens

### Running Service

```bash
# Using UV (recommended)
uv run uvicorn main:app --reload --port 8000

# Alternative: Traditional
uvicorn main:app --reload --port 8000
```

### Running Tests

```bash
# Using UV
uv run pytest app/tests

# Alternative: Traditional
pytest app/tests
```
