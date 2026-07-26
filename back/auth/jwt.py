from datetime import timedelta
import jwt
import os
from fastapi import APIRouter, HTTPException,Depends,Response
from sqlmodel import Session
from starlette.requests import Request
from back.db.auth_user_db import datetime_now
router = APIRouter(prefix="/jwt", tags=["auth"])
EXP_HOURS=24
private_key = os.getenv("JWT_SECRET")
from back.db.database import get_session
from back.db.auth_user_db import User

COOKIE_NAME = "access_token"

def token_encode(user_id):
    token=jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime_now() + timedelta(hours=EXP_HOURS),
            "iat": datetime_now(),
        },
        key=private_key,
        algorithm="HS256",
    )
    return token

def token_decode(token):
    try:
        payload=jwt.decode(token, key=private_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")



def token_give(auth,request: Request,response: Response):
    token = token_encode(auth.user_id)
    response.set_cookie(key=COOKIE_NAME, value=token, httponly=True, samesite="lax", max_age=EXP_HOURS * 3600, )

def get_user_id_from_token(request: Request,session: Session = Depends(get_session)):
    token = request.headers.get(COOKIE_NAME)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id=token_decode(token).get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user=session.get(User, int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user.id
