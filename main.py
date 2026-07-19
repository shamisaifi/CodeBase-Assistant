from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from db.session import engine
from db.base import Base
from routes.auth_router import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("DB tables are created")

    yield

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

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])


# exceptions handled in the last
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
