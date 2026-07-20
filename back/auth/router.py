from http.client import HTTPException
from authlib.integrations.base_client.errors import MismatchingStateError,OAuthError
from fastapi import APIRouter, Request, HTTPException
from .oauth import oauth

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/g")
async def google_login(request: Request):
    return await oauth.google.authorize_redirect(request, redirect_uri="http://localhost:8000/auth/g/callback")

@router.get("/g/callback")
async def google_login_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except (MismatchingStateError,OAuthError):
        raise HTTPException(status_code=400, detail="Please try again.")
    userinfo= token["userinfo"]
    return userinfo