from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.services import UserService
from app.services.services import TransactionService
from app.services.services import InventoryService
from app.db.database import get_db
from jose import jwt, JWTError
from pydantic import BaseModel, Field


router = APIRouter(prefix="/api")


SECRET_KEY = "my_secret_key"
ALGORITHM = "HS256"


def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

class SendCoinRequest(BaseModel):
    toUser: str
    amount: int = Field(gt=0)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    user = await service.authenticate_user(
        username=form_data.username,
        password=form_data.password
    )

    token = jwt.encode(
        {"user_id": user.id},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }

class RegisterRequest(BaseModel):
    username: str
    password: str

@router.post("/register")
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    user = await service.create_user(
        username=data.username,
        password=data.password
    )

    return {
        "id": user.id,
        "username": user.username
    }


async def get_current_user_id(token: str = Depends(oauth2_scheme)):
    payload = decode_jwt(token)
    return payload["user_id"]



@router.get("/info")
async def get_info(
    user_id: int = Depends(get_current_user_id), 
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)

    user = await service.get_user(user_id)
    return user


@router.post("/sendCoin", status_code= status.HTTP_200_OK)
async def send_coin(
    data: SendCoinRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = TransactionService(db)

    await service.send_coin(
        from_user_id=user_id,
        to_username=data.toUser,
        amount=data.amount
    )

@router.get("/buy/{item}")
async def but_item(
    item:str,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = InventoryService(db)

    await service.buy_item(
        item_name = item,
        user_id = user_id
    )

    