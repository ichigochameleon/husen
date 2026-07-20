from typing import List, Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select, JSON, Relationship



class Project(SQLModel, table=True):
    __tablename__ = "project"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    overview: Optional[str] = None
    mainchat_url: Optional[str] = None
    mainrepo_url: Optional[str] = None
    others_url: List[str] = Field(default_factory=list, sa_type=JSON)
    memos: List["Memo"] = Relationship(back_populates="project")


class Memo(SQLModel, table=True):
    __tablename__ = "memo"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    kinds: Optional[int] = None
    others_kinds: Optional[str] = None
    text: Optional[str] = None
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    project: Optional[Project] = Relationship(back_populates="memos")


class ProjectCreate(SQLModel):
    name: str
    overview: Optional[str] = None
    mainchat_url: Optional[str] = None
    mainrepo_url: Optional[str] = None
    others_url: List[str] = Field(default_factory=list)


class MemoCreate(SQLModel):
    name: str
    kinds: Optional[int] = None
    others_kinds: Optional[str] = None
    text: Optional[str] = None


class MemoUpdate(SQLModel):
    name: Optional[str] = None
    kinds: Optional[int] = None
    others_kinds: Optional[str] = None
    text: Optional[str] = None


class ProjectUpdate(SQLModel):
    name: Optional[str] = None
    overview: Optional[str] = None
    mainchat_url: Optional[str] = None
    mainrepo_url: Optional[str] = None
    others_url: Optional[List[str]] = None


class MemoRes(SQLModel):
    id: int
    name: str
    kinds: Optional[int] = None
    others_kinds: Optional[str] = None
    text: Optional[str] = None
    project_id: Optional[int] = None


class ProjectRes(SQLModel):
    id: int
    name: str
    overview: Optional[str] = None
    mainchat_url: Optional[str] = None
    mainrepo_url: Optional[str] = None
    others_url: List[str] = Field(default_factory=list)
    memos: List[MemoRes] = Field(default_factory=list)
