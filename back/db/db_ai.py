from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


class ProgressEnum(str, Enum):
    NOT_STARTED = "未完了"
    IN_PROGRESS = "途中結論"
    COMPLETED = "完了"


class ProjectUserLink(SQLModel, table=True):
    __tablename__ = "project_user_link"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    project_id: int = Field(foreign_key="project.id", ondelete="CASCADE")
    role: str = Field(default="member")  # 例: admin, member など


# ==========================================
# 2. メインテーブル定義
# ==========================================
class Auth(SQLModel, table=True):
    """authテーブル: 認証情報を管理"""

    __tablename__ = "auth"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    last_login_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    provider: str  # 例: "google", "github", "email"
    provider_user_id: str  # 各プロバイダ側での一意なID

    # 外部キー関係（ユーザーdbへの電線）
    user: "User" = Relationship(back_populates="auths")


class User(SQLModel, table=True):
    """ユーザーdb"""

    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    icon: Optional[str] = None
    overview: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    update_at: datetime = Field(default_factory=datetime.utcnow)
    active: bool = Field(default=True)

    # 外部キー関係（Relationship）
    auths: List[Auth] = Relationship(back_populates="user")
    chats: List["Chat"] = Relationship(back_populates="user")

    # 参加dbを経由して、自分が参加しているプロジェクト一覧を直接取得できるマジック
    projects: List["Project"] = Relationship(
        back_populates="users", link_model=ProjectUserLink
    )


class Project(SQLModel, table=True):
    """プロジェクトdb"""

    __tablename__ = "project"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    overview: Optional[str] = None
    mainchat_url: Optional[str] = None
    mainrepo_url: Optional[str] = None
    others_url: List[str] = Field(
        default_factory=list, sa_type=SQLModel.metadata.naming_convention
    )  # JSONや文字列リスト等、用途に合わせて調整してください

    # 外部キー関係（Relationship）
    memos: List["Memo"] = Relationship(back_populates="project")

    # 参加dbを経由して、プロジェクトに参加しているユーザー一覧を直接取得できるマジック
    users: List[User] = Relationship(
        back_populates="projects", link_model=ProjectUserLink
    )


class Memo(SQLModel, table=True):
    """メモdb"""

    __tablename__ = "memo"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    kinds: Optional[int] = None
    others_kinds: Optional[str] = None
    text: Optional[str] = None
    progress: ProgressEnum = Field(default=ProgressEnum.NOT_STARTED)

    # 親であるプロジェクトへの外部キー
    project_id: int = Field(foreign_key="project.id", ondelete="CASCADE")

    # 外部キー関係（Relationship）
    project: Project = Relationship(back_populates="memos")
    chats: List["Chat"] = Relationship(back_populates="memo")


class Chat(SQLModel, table=True):
    """チャットdb"""

    __tablename__ = "chat"

    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 外部キー（誰が、どのメモに書いたか）
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    memo_id: int = Field(foreign_key="memo.id", ondelete="CASCADE")

    # 外部キー関係（Relationship）
    memo: Memo = Relationship(back_populates="chats")
    user: User = Relationship(
        back_populates="chats"
    )  # 画面にアイコンや名前を出すために必須
