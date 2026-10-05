from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.user import router as user_router

from app.services.services_errors import (UserNotFoundError,
                                            NotEnoughCoinsError,
                                            SelfTransferError,
                                            ItemNotFoundError
                                        )

from contextlib import asynccontextmanager
from app.cache.cache import redis_cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_cache.init()
    yield
    await redis_cache.close()


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"errors": str(exc)},
    )


@app.exception_handler(NotEnoughCoinsError)
async def not_enough_coins_handler(request: Request, exc: NotEnoughCoinsError):
    return JSONResponse(
        status_code=400,
        content={"errors": str(exc)},
    )

@app.exception_handler(SelfTransferError)
async def self_transfer_handler(request: Request, exc: SelfTransferError):
    return JSONResponse(
        status_code=400,
        content={"errors": str(exc)}
    )


@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc:ItemNotFoundError):
    return JSONResponse(
        status_code=400,
        content={"errors": str(exc)}
    )
