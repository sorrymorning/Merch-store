# Merch Store

Merch Store is a FastAPI-based backend for a virtual merchandise store with user accounts, coin balance management, purchase logic, inventory tracking, transaction history, and a simple analytics dashboard.

The project demonstrates core backend patterns such as:
- FastAPI REST API
- async SQLAlchemy
- PostgreSQL / SQLite support
- Redis caching
- JWT authentication
- Alembic migrations
- Docker Compose deployment
- Streamlit dashboard for analytics
- pytest-based testing

## Overview

The application allows users to:
- register and log in
- receive a starting coin balance
- send coins to other users
- buy merchandise
- view their inventory and transaction history
- inspect sales analytics via dashboard

## Tech Stack

- Python 3.12+
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- SQLite
- Redis
- Alembic
- JWT (python-jose)
- Streamlit
- Pytest
- Docker & Docker Compose

## How to run

### Option 1: Docker Compose (recommended)

1. Create environment file:
```bash
cp .env.example .env
```

2. Start containers:
```bash
docker compose up --build
```

3. API is available at:
```text
http://localhost:8001
```

4. Swagger docs:
```text
http://localhost:8001/docs
```

5. Streamlit dashboard:
```text
http://localhost:8501
```

### Option 2: Local development

1. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env`:
```bash
cp .env.example .env
```

4. Start FastAPI app:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Open docs:
```text
http://localhost:8000/docs
```

## Project architecture

The codebase is split into a simple layered structure:

- API layer: `app/api/user.py`
- Business logic: `app/services/services.py`
- Repository layer: `app/repositories/repository.py`
- Models: `app/models/models.py`
- Database connection: `app/db/database.py`
- Configuration: `app/core/config.py`
- Cache: `app/cache/cache.py`
- Analytics: `analytics.py`

## API endpoints

Base path: `/api`

### Authentication

#### POST `/api/register`
Register a new user.

Request:
```json
{
  "username": "username",
  "password": "secret123"
}
```

Response:
```json
{
  "id": 1,
  "username": "username"
}
```

#### POST `/api/login`
Authenticate the user and get a JWT token.

Request form data:
```text
username=username
password=secret123
```

Response:
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

### User

#### GET `/api/info`
Returns user details and history. Requires JWT.

Headers:
```http
Authorization: Bearer <token>
```

Response:
```json
{
  "coins": 500,
  "inventory": [
    { "type": "cup", "quantity": 2 }
  ],
  "coinHistory": {
    "received": [
      { "fromUser": "alice", "amount": 25 }
    ],
    "sent": [
      { "toUser": "bob", "amount": 10 }
    ]
  }
}
```

### Transactions

#### POST `/api/sendCoin`
Transfer coins to another user.

Request:
```json
{
  "toUser": "bob",
  "amount": 50
}
```

Response:
```json
{
  "status": "success"
}
```

### Products

#### POST `/api/add_item`
Create a merchandise item.

Request:
```json
{
  "merch_name": "cap",
  "merch_price": 150
}
```

#### POST `/api/buy/{item}`
Buy product by item name.

Example:
```bash
POST /api/buy/cap
```

### Health

#### GET `/health`
Returns a basic health response.

```json
{
  "status": "ok"
}
```


## TODO / Planned improvements

This project has room for improvement before it is ready for a production-grade portfolio presentation:

- [ ] Store passwords using bcrypt or argon2 instead of plain text
- [ ] Add robust exception handling and HTTP status mapping
- [ ] Add validation schemas for all request/response models
- [ ] Split `user.py` into separated routers for auth, users, transactions, and items
- [ ] Improve Redis cache abstraction and key naming
- [ ] Add structured logging with request IDs and operation tracking
- [ ] Add more tests for invalid auth, duplicate users, and invalid token cases
- [ ] Add concurrency tests for parallel purchases and transfers
- [ ] Add a proper auth service and refresh-token flow
- [ ] Add CI/CD with pytest, ruff, black, and GitHub Actions
- [ ] Add README architecture diagram and example flows
- [ ] Add categories, stock control, discounts, and item metadata
- [ ] Improve the analytics dashboard with empty-state handling and richer metrics
- [ ] Review DB indexes and performance for higher-load scenarios
- [ ] Remove hardcoded secrets and secure env configuration
- [ ] Add better health checks for database and Redis readiness

