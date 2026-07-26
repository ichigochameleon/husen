import datetime
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel,Relationship

def datetime_now():
    return datetime.datetime.now(datetime.timezone.utc)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str= Field(index=True)
    icon: Optional[bytes] = Field(default=None)
    overview: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime_now)
    update_at:datetime.datetime=Field(default_factory=datetime_now)
    active: bool = Field(default=True)
    auths: list["Auth"]= Relationship(back_populates="user")

class Auth(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id"),
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    last_login_at: datetime.datetime = Field(default_factory=datetime_now)
    provider: str= Field(index=True)
    provider_user_id: str= Field(index=True)
    user: "User" = Relationship(back_populates="auths")