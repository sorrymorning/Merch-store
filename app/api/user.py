


from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.services import UserService
from app.services.services import TransactionService
from app.services.services import PurchaseService
from app.db.database import get_db


from pydantic import BaseModel, Field

class SendCoinRequest(BaseModel):
    toUser: str
    amount: int = Field(gt=0)


# разобраться в этом!!!
async def get_current_user_id(token: str = Depends(oauth2_scheme)):
    payload = decode_jwt(token)
    return payload["user_id"]

router = APIRouter(prefix="/api")


@router.get("/info")
async def get_info(user_id:int, db: AsyncSession = Depends(get_db)):
    service = UserService(db)

    user = await service.get_user(user_id)

    if not user:
        raise HTTPException(status_code = 404)
    return user


@router.post("/sendCoin", response_model= status.HTTP_200_OK)
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
    service = PurchaseService(db)

    await service.buy_item(
        item_name = item,
        user_id = user_id
    )

    