from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.orm import selectinload
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
import os
from back.db.husen_memo_db import (
    Project,
    Memo,
    ProjectCreate,
    MemoCreate,
    MemoUpdate,
    ProjectUpdate,
    MemoRes,
    ProjectRes,
)
from auth.router import router as auth_router

load_dotenv()

sqlite_file_name = "banana.db"
BASE_DIR = Path(__file__).resolve().parent
sqlite_url = f"sqlite:///{BASE_DIR /'db'/'banana.db'}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


origins = ["http://localhost", "http://localhost:8080", "http://localhost:5173"]


app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY"),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

def create_db():
    SQLModel.metadata.create_all(engine)


@app.on_event("startup")
def start():
    create_db()


def get_session():
    with Session(engine) as session:
        yield session


@app.get("/projects/", response_model=List[ProjectRes],tags=["projects"])
def read_projects(session: Session = Depends(get_session)):
    statement = select(Project).options(selectinload(Project.memos))
    projects = session.exec(statement).all()
    return projects


@app.post("/projects/", response_model=ProjectRes, tags=["projects"])
def create_project(project: ProjectCreate, session: Session = Depends(get_session)):
    project_obj = Project(**project.model_dump())
    session.add(project_obj)
    session.commit()
    session.refresh(project_obj)
    return project_obj


@app.put("/projects/{project_id}", response_model=ProjectRes, tags=["projects"])
def update_project(
    new_project: ProjectUpdate, project_id: int, session: Session = Depends(get_session)
):
    old_project = session.get(Project, project_id)
    if not old_project:
        raise HTTPException(status_code=404, detail="Project not found")
    update_data = new_project.model_dump(exclude_unset=True)
    old_project.sqlmodel_update(update_data)
    session.add(old_project)
    session.commit()
    session.refresh(old_project)
    return old_project


@app.get("/projects/{project_id}", response_model=ProjectRes, tags=["projects"])
def read_project(project_id: int, session: Session = Depends(get_session)):
    statement = (
        select(Project)
        .options(selectinload(Project.memos))
        .where(Project.id == project_id)
    )
    project = session.exec(statement).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@app.delete("/projects/{project_id}", tags=["projects"])
def delete_project(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    session.delete(project)
    session.commit()
    return {"detail": "Project deleted"}


@app.post("/projects/{project_id}/memos", response_model=MemoRes, tags=["memos"])
def create_project_memo(
    project_id: int, memo: MemoCreate, session: Session = Depends(get_session)
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    memo_data = memo.model_dump()
    memo_data["project_id"] = project_id

    memo_obj = Memo(**memo_data)

    session.add(memo_obj)
    session.commit()
    session.refresh(memo_obj)

    return memo_obj


@app.put("/memos/{memo_id}", response_model=MemoRes, tags=["memos"])
def update_project_memo(
    memo_id: int, new_memo: MemoUpdate, session: Session = Depends(get_session)
):
    old_memo = session.get(Memo, memo_id)
    if not old_memo:
        raise HTTPException(status_code=404, detail="Project or Memo not found")
    update_data = new_memo.model_dump(exclude_unset=True)
    old_memo.sqlmodel_update(update_data)
    session.add(old_memo)
    session.commit()
    session.refresh(old_memo)
    return old_memo


@app.delete("/memos/{memo_id}", tags=["memos"])
def delete_project_memo(memo_id: int, session: Session = Depends(get_session)):
    memo = session.get(Memo, memo_id)
    if not memo:
        raise HTTPException(status_code=404, detail="Project or Memo not found")
    session.delete(memo)
    session.commit()
    return {"detail": "Memo deleted"}
