from datetime import datetime, timedelta, timezone
import jwt
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

