from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.services import (UserService,
                                TransactionService,
                                InventoryService,
                                MerchService
)
from app.db.database import get_db
from jose import jwt, JWTError
from pydantic import BaseModel, Field
from app.core.config import settings

router = APIRouter(prefix="/api")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

class SendCoinRequest(BaseModel):
    toUser: str
    amount: int = Field(gt=0)

class CreateItemRequest(BaseModel):
    merch_name:str
    merch_price:int = Field(gt=0)



def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def get_current_user_id(token: str = Depends(oauth2_scheme)):
    payload = decode_jwt(token)
    user_id: int | None = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return user_id



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

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )

    token = jwt.encode(
        {"user_id": user.id},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/register", , status_code=status.HTTP_201_CREATED)
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
    return {"status": "success"}


@router.post("/add_item", status_code= status.HTTP_201_CREATED)
async def add_item(
    item: CreateItemRequest,
    db: AsyncSession = Depends(get_db)
):
    service = MerchService(db)

    await service.create_item(
        merch_name=item.merch_name,
        merch_price=item.merch_price
    )

    return {"status": "created"}

@router.post("/buy/{item}")
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

    
