from authlib.integrations.base_client.errors import MismatchingStateError,OAuthError
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlmodel import Session, select
from back.db.database import get_session
from back.auth.oauth import oauth
from back.db.auth_user_db import User,Auth
from back.db.auth_user_db import datetime_now

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/google")
async def google_login(request: Request):
    return await oauth.google.authorize_redirect(request, redirect_uri="http://localhost:8000/auth/google/callback")

@router.get("/google/callback")
async def google_login_callback(request: Request,session: Session = Depends(get_session)):
    try:
        token = await oauth.google.authorize_access_token(request)
    except (MismatchingStateError,OAuthError):
        raise HTTPException(status_code=400, detail="Please try again.")
    userinfo= token["userinfo"]
    auth=(session.exec(select(Auth).where(
        Auth.provider=="google",
        Auth.provider_user_id==str(userinfo["sub"])))
          .first()
          )
    if auth:
        auth.last_login_at =datetime_now()
        session.add(auth)
        session.commit()
        return 201
    else:
        user=User(username=userinfo.get("name"))
        session.add(user)
        session.commit()
        session.refresh(user)

        auth=Auth(
            user_id=user.id,
            provider="google",
            provider_user_id=str(userinfo["sub"]),
        )
        session.add(auth)
        session.commit()
        return 200

@router.get("/github")
async def github_login(request: Request):
    return await oauth.github.authorize_redirect(request, redirect_uri="http://localhost:8000/auth/github/callback")

@router.get("/github/callback")
async def github_login_callback(request: Request,session: Session = Depends(get_session)):
    try:
        token = await oauth.github.authorize_access_token(request)
    except (MismatchingStateError,OAuthError):
        raise HTTPException(status_code=400, detail="Please try again.")
    userinfo = await oauth.github.get('user', token=token)
    userinfo=userinfo.json()
    auth = (session.exec(
        select(Auth).where(
            Auth.provider == "github",
            Auth.provider_user_id == str(userinfo["id"])
            )
        ).first()
    )
    if auth:
        auth.last_login_at = datetime_now()
        session.add(auth)
        session.commit()
        return 201
    else:
        user=User(username=userinfo.get("name") or userinfo.get("login"),)
        session.add(user)
        session.commit()
        session.refresh(user)
        auth=Auth(
            user_id=user.id,
            provider="github",
            provider_user_id=str(userinfo["id"]),
        )
        session.add(auth)
        session.commit()
    return 200