from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.settings import settings
from db.base import Base
from db.session import engine
from routes.auth_router import router as auth_router
from routes.chat_router import router as chat_router
from routes.file_router import router as file_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("DB tables are created")

    app.state.redis = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,
        decode_responses=True
    )

    yield

    await app.state.redis.aclose()
    await engine.dispose()
    print("DB connections closed")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# router will come here when declared
@app.get("/")
def home():
    return JSONResponse({
        "status": 200,
        "message": "this is home"
    })

app.include_router(auth_router, prefix="/api/v1/auth", tags=["uth"])
app.include_router(file_router, prefix="/api/v1/files", tags=["Files"])
app.include_router(chat_router, prefix="/api/v1/chat", tags=["chat"])


# exceptions handled in the last
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
