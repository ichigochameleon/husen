from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, JSON


def datetime_now():
    return datetime.now(timezone.utc)


class ProgressStatus(str, Enum):
    NOT_STARTED = "未完了"
    IN_PROGRESS = "途中結論"
    COMPLETED = "完了"


class ProjectUserLinkBase(SQLModel):
    project_id: int = Field(foreign_key="project.id", ondelete="CASCADE")
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    role: str = Field(index=True, default="member")


class ProjectUserLink(ProjectUserLinkBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)


class UserBase(SQLModel):
    username: str = Field(index=True)
    icon: Optional[str] = None
    overview: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: datetime = Field(default_factory=datetime_now)
    active: bool = Field(default=True)


class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    auths: List["Auth"] = Relationship(back_populates="user")
    chats: List["Chat"] = Relationship(back_populates="user")
    memos: List["Memo"] = Relationship(back_populates="user")
    projects: List["Project"] = Relationship(back_populates="users", link_model=ProjectUserLink)


class AuthBase(SQLModel):
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    last_login_at: datetime = Field(default_factory=datetime_now)
    provider: str
    provider_user_id: int


class Auth(AuthBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user: "User" = Relationship(back_populates="auths")


class ProjectBase(SQLModel):
    name: str = Field(index=True)
    overview: Optional[str] = None
    mainchat_url: Optional[str] = None
    mainrepo_url: Optional[str] = None
    others_url: List[str] = Field(default_factory=list, sa_type=JSON)
    status: ProgressStatus = Field(index=True, default=ProgressStatus.NOT_STARTED)


class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    users: List["User"] = Relationship(back_populates="projects", link_model=ProjectUserLink)
    memos: List["Memo"] = Relationship(back_populates="project")


class MemoBase(SQLModel):
    name: str = Field(index=True)
    kinds: Optional[int] = Field(index=True, default=None)
    other_kinds: Optional[str] = Field(default=None)
    text: Optional[str] = Field(index=False, default=None)
    project_id: int = Field(default=None, foreign_key="project.id", ondelete="CASCADE")
    user_id: int = Field(default=None, foreign_key="user.id", ondelete="CASCADE")


class Memo(MemoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    project: "Project" = Relationship(back_populates="memos")
    user: "User" = Relationship(back_populates="memos")
    chats: List["Chat"] = Relationship(back_populates="memo")


class ChatBase(SQLModel):
    text: Optional[str] = Field(index=False, default=None)
    created_at: datetime = Field(default_factory=datetime_now)

    memo_id: int = Field(foreign_key="memo.id", ondelete="CASCADE")
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")


class Chat(ChatBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    memo: Optional["Memo"] = Relationship(back_populates="chats")
    user: "User" = Relationship(back_populates="chats")
