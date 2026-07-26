from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Request

from config.settings import settings


def generateAccessToken(payload):
    
    payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=5)
    payload["iat"] = datetime.now(timezone.utc)

    accesssToken = jwt.encode(payload, settings.ACCESS_TOKEN_SECRET, algorithm="HS256")
    return accesssToken

def generateRefreshToken(payload):

    payload["exp"] = datetime.now(timezone.utc) + timedelta(days=7)
    payload["iat"] = datetime.now(timezone.utc)

    refreshToken = jwt.encode(payload, settings.REFRESH_TOKEN_SECRET, algorithm="HS256")
    return refreshToken


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "Unknown"