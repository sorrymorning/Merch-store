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

This repository is suitable as a portfolio project because it combines several production-relevant concepts:
- API layer
- service layer
- repository layer
- data models
- business logic validation
- caching
- observability basics
- Docker setup

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

## Project Structure

```text
.
├── app/
│   ├── api/
│   │   └── user.py
│   ├── cache/
│   │   └── cache.py
│   ├── core/
│   │   ├── config.py
│   │   └── logger.py
│   ├── db/
│   │   └── database.py
│   ├── models/
│   │   └── models.py
│   ├── repositories/
│   │   └── repository.py
│   ├── services/
│   │   ├── services.py
│   │   └── services_errors.py
│   ├── main.py
│   └── __init__.py
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── tests/
│   ├── conftest.py
│   ├── test_integration.py
│   └── test_services.py
├── analytics.py
├── .env.example
├── .env.test
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
├── create_view.sql
├── alembic.ini
├── prestart.sh
├── .gitignore
├── README.md
└── LICENSE (optional)
```

## How it works

### 1. User flow
- User registers via `/api/register`
- User logs in via `/api/login`
- JWT token is returned
- Token is used to access protected routes

### 2. Coin transfer flow
- User sends coins to another user
- Server validates:
  - sender exists
  - receiver exists
  - sender is not giving to themselves
  - amount is positive
  - sender has enough balance
- Transaction is recorded in the database
- User cache is invalidated

### 3. Product purchase flow
- User buys an item by name
- App checks:
  - user exists
  - item exists
  - user has enough coins
- Item gets added to inventory
- Purchase history is saved
- User data cache is invalidated

### 4. Caching
Redis is used to cache frequently requested information, such as:
- user profiles
- merch data

This reduces repeated database reads and helps improve performance.

### 5. Analytics dashboard
The `analytics.py` file contains a Streamlit dashboard that reads the `product_sales_mart` table and displays:
- revenue by product
- sold items
- number of buyers
- sales overview

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

This structure keeps responsibilities separated and makes it easier to understand the domain and extend the app.

## API endpoints

Base path: `/api`

### Authentication

#### POST `/api/register`
Register a new user.

Request:
```json
{
  "username": "amir",
  "password": "secret123"
}
```

Response:
```json
{
  "id": 1,
  "username": "amir"
}
```

#### POST `/api/login`
Authenticate the user and get a JWT token.

Request form data:
```text
username=amir
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

## Testing strategy

The project includes a `pytest`-based test suite for validation of core logic.

### Run tests
```bash
pytest -q
```

### Run a specific file
```bash
pytest tests/test_services.py -q
```

### Existing testing approach
The project uses:
- async fixtures
- mocked repositories
- service-level validation
- FastAPI test client patterns

This helps validate:
- happy path flows
- validation on not found cases
- transfer restrictions
- item purchasing logic

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

## Notes

This project is a good foundation for a portfolio because it already includes:
- FastAPI
- async SQLAlchemy
- JWT auth
- Redis cache
- Docker support
- basic analytics dashboard

It still needs a few production-ready improvements, but it clearly demonstrates practical backend development skills.

## License

This project does not currently declare a license. If you plan to publish it publicly, consider adding an MIT or Apache 2.0 license.
