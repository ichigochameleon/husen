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

#権限
class ProjectPermission(str, Enum):
    READ="read"
    UPDATE="update"
    DELETE="delete"
    MANAGE_READ="manage_read"
    MANAGE_UPDATE="manage_update"
    MANAGE_DELETE="manage_delete"
    OWNER="owner"
    STAR="star"

class ProjectExit(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"

class ProjectUserLinkBase(SQLModel):
    project_id: int = Field(foreign_key="project.id", ondelete="CASCADE")
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    permission:List[ProjectPermission] = Field(default_factory=list,sa_type=JSON)

class ProjectUserLink(ProjectUserLinkBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class UserBase(SQLModel):
    username: str = Field(index=True)
    icon: Optional[str] = None
    overview: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    active: bool

class UserUpdate(SQLModel):
    username: Optional[str] = None
    icon: Optional[str] = None
    overview: Optional[str] = None
    active: Optional[bool] = None

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    auths: List["Auth"] = Relationship(back_populates="user")
    chats: List["Chat"] = Relationship(back_populates="user")
    memos: List["Memo"] = Relationship(back_populates="user")
    projects: List["Project"] = Relationship(back_populates="users", link_model=ProjectUserLink)

    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: datetime = Field(default_factory=datetime_now)
    active: bool = Field(default=True)


class AuthBase(SQLModel):
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    last_login_at: datetime = Field(default_factory=datetime_now)
    provider: str
    provider_user_id: str


class Auth(AuthBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user: "User" = Relationship(back_populates="auths")


class ProjectBase(SQLModel):
    name: str = Field(index=True)
    overview: Optional[str] = None
    mainchat_url: Optional[str] = None
    mainrepo_url: Optional[str] = None
    others_url: List[str] = Field(default_factory=list, sa_type=JSON)
    status: ProgressStatus
    project_exist:ProjectExit=Field(default=ProjectExit.PRIVATE)

class ProjectCreate(ProjectBase):
    pass

class ProjectRead(ProjectBase):
    id: int

class ProjectUpdate(SQLModel):
    name: Optional[str] = None
    overview: Optional[str] = None
    mainchat_url: Optional[str] = None
    mainrepo_url: Optional[str] = None
    others_url: Optional[List[str]] = None
    status: Optional[ProgressStatus] = None
    project_exist: Optional[ProjectExit]= None

class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    users: List["User"] = Relationship(back_populates="projects", link_model=ProjectUserLink)
    memos: List["Memo"] = Relationship(back_populates="project")




class MemoBase(SQLModel):
    name: str = Field(index=True)
    kinds: Optional[int] = Field(index=True, default=None)
    other_kinds: Optional[str] = Field(default=None)
    text: Optional[str] = Field(index=False, default=None)

class MemoCreate(MemoBase):
    pass

class MemoRead(MemoBase):
    id: int
    project_id: int
    user_id: int
    created_at: datetime

class MemoUpdate(SQLModel):
    name: Optional[str] = None
    kinds: Optional[int] = None
    other_kinds: Optional[str] = None
    text: Optional[str] = None

class Memo(MemoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    project_id: int = Field(default=None, foreign_key="project.id", ondelete="CASCADE")
    user_id: int = Field(default=None, foreign_key="user.id", ondelete="CASCADE")

    project: "Project" = Relationship(back_populates="memos")
    user: "User" = Relationship(back_populates="memos")
    chats: List["Chat"] = Relationship(back_populates="memo")

    created_at: datetime = Field(default_factory=datetime_now)


class ChatBase(SQLModel):
    text: Optional[str] = Field(index=False, default=None)

class ChatCreate(ChatBase):
    pass

class ChatRead(ChatBase):
    id: int
    memo_id: int
    user_id: int
    created_at: datetime

class ChatUpdate(SQLModel):
    text: Optional[str] = None


class Chat(ChatBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    created_at: datetime = Field(default_factory=datetime_now)

    memo_id: int = Field(default=None, foreign_key="memo.id", ondelete="CASCADE")
    user_id: int = Field(default=None, foreign_key="user.id", ondelete="CASCADE")

    memo: Optional["Memo"] = Relationship(back_populates="chats")
    user: "User" = Relationship(back_populates="chats")
