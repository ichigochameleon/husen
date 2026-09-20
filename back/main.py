from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session,select
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
import os
from typing import List
from back.auth.jwt_tools import get_user_id_from_token
from back.db.db_base import (
    Project,
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
    Memo,
    MemoCreate,
    MemoRead,
    MemoUpdate,
    ProjectUserLink,
    ChatRead,
    Chat,
    ChatUpdate,
    UserRead,
    User,
    UserUpdate,
    ProjectPermission
)
from back.auth.router import router as auth_router
from back.db.database import create_db, get_session
from back.permission import (
    check_project_permission,
    check_project_write_permission,
    check_project_delete_permission,
    check_project_read_permission, check_project_manage_read_permission, check_project_manage_update_permission,
    check_project_manage_delete_permission, check_project_owner_permission
)
load_dotenv()

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

@app.on_event("startup")
def start():
    create_db()

@app.get("/user", response_model=UserRead, tags=["user"])
def read_user(session: Session = Depends(get_session), current_user_id= Depends(get_user_id_from_token)):
    statement = select(User).where(User.id == current_user_id)
    user = session.exec(statement).first()
    return user

@app.get("/users/{user_id}", response_model=UserRead, tags=["user"])
def read_other_user(user_id: int, session: Session = Depends(get_session), current_user_id=Depends(get_user_id_from_token)):
    if user_id == current_user_id:
        return RedirectResponse(url="/user", status_code=302)
    user=session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/user", response_model=UserRead, tags=["user"])
def update_user(new_user:UserUpdate,session: Session = Depends(get_session),current_user_id = Depends(get_user_id_from_token)):
    current_user=session.get(User, current_user_id)
    for key, value in new_user.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user
@app.delete("/user",tags=["user"])
def delete_user(current_user_id=Depends(get_user_id_from_token), session: Session = Depends(get_session)):
    current_user_id=session.get(User, current_user_id)
    session.delete(current_user_id)
    session.commit()
    return {"detail": "User deleted"}


@app.get("/projects/", response_model=List[ProjectRead], tags=["projects"])
def read_projects(
    session: Session = Depends(get_session),
    current_user_id=Depends(get_user_id_from_token)
):
    statement = (
        select(Project)
        .join(ProjectUserLink)
        .where(
            ProjectUserLink.user_id == current_user_id,
            ProjectUserLink.permission != []
        )
    )

    projects = session.exec(statement).all()
    return projects

@app.post("/projects/", response_model=ProjectRead, tags=["projects"])
def create_project(project: ProjectCreate, session: Session = Depends(get_session),current_user_id=Depends(get_user_id_from_token)):
    project_obj = Project(**project.model_dump())
    session.add(project_obj)
    session.flush()
    link=ProjectUserLink(project_id=project_obj.id, user_id=current_user_id,permission=[
        ProjectPermission.READ,
        ProjectPermission.UPDATE,
        ProjectPermission.DELETE,
        ProjectPermission.MANAGE_READ,
        ProjectPermission.MANAGE_UPDATE,
        ProjectPermission.MANAGE_DELETE,
        ProjectPermission.OWNER
    ]
                         )
    session.add(link)
    session.commit()
    return project_obj


@app.put("/projects/{project_id}", response_model=ProjectRead, tags=["projects"])
def update_project(
    new_project: ProjectUpdate, project_id: int, session: Session = Depends(get_session),current_user_id=Depends(get_user_id_from_token)
):
    old_project = session.get(Project, project_id)
    if not old_project:
        raise HTTPException(status_code=404, detail="Project not found")
    check_project_write_permission(project_id, current_user_id, session)
    update_data = new_project.model_dump(exclude_unset=True)
    old_project.sqlmodel_update(update_data)
    session.add(old_project)
    session.commit()
    session.refresh(old_project)
    return old_project


@app.get("/projects/{project_id}", response_model=ProjectRead, tags=["projects"])
def read_project(project_id: int, session: Session = Depends(get_session), current_user_id=Depends(get_user_id_from_token)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    check_project_read_permission(project_id, current_user_id, session)
    return project

@app.delete("/projects/{project_id}", tags=["projects"])
def delete_project(project_id: int, session: Session = Depends(get_session),current_user_id=Depends(get_user_id_from_token)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    check_project_delete_permission(project_id, current_user_id, session)
    session.delete(project)
    session.commit()
    return {"detail": "Project deleted"}

@app.post("/projects/{project_id}/star", tags=["projects"])
def star_project(project_id: int, session: Session = Depends(get_session), current_user_id=Depends(get_user_id_from_token)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    check_project_read_permission(project_id, current_user_id, session)
    link = session.exec(select(ProjectUserLink).where(ProjectUserLink.user_id == current_user_id,
                                                      ProjectUserLink.project_id == project_id)).first()
    if not link:
        link = ProjectUserLink(project_id=project_id, user_id=current_user_id,permission=[])
        session.add(link)
    if ProjectPermission.STAR in link.permission:
        return {"detail": "Project already starred"}
    link.permission.append(ProjectPermission.STAR)
    session.commit()
    session.refresh(link)
    return {"detail": "Project starred"}

@app.delete("/projects/{project_id}/star", tags=["projects"])
def unstar_project(project_id: int, session: Session = Depends(get_session), current_user_id=Depends(get_user_id_from_token)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    check_project_read_permission(project_id, current_user_id, session)
    link = session.exec(select(ProjectUserLink).where(ProjectUserLink.user_id == current_user_id,
                                                      ProjectUserLink.project_id == project_id)).first()
    if not link:
        raise HTTPException(status_code=404, detail="Project not starred")
    if ProjectPermission.STAR not in link.permission:
        return {"detail": "Project not starred"}
    link.permission.remove(ProjectPermission.STAR)
    session.commit()
    session.refresh(link)
    return {"detail": "Project unstarred"}

@app.get("/projects/{project_id}/permissions",tags=["projects"])
def read_project_permissions(project_id: int, session: Session = Depends(get_session), current_user_id=Depends(get_user_id_from_token)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    link = session.exec(select(ProjectUserLink).where(ProjectUserLink.project_id == project_id, ProjectUserLink.user_id == current_user_id)).first()
    if not link:
        return {"permissions": []}
    return {"permissions": link.permission}

@app.get("/projects/{project_id}/other_permissions",tags=["projects"])
def read_project_other_permissions(project_id: int, assign_user_id:int, session: Session = Depends(get_session), current_user_id=Depends(get_user_id_from_token),):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if current_user_id == assign_user_id:
        return RedirectResponse(url=f"/projects/{project_id}/permissions", status_code=302)
    link = session.exec(select(ProjectUserLink).where(ProjectUserLink.project_id == project_id, ProjectUserLink.user_id == assign_user_id)).first()
    if not link:
        return {"permissions": []}
    return {"permissions": link.permission}


def project_permission_give(permission_kind:ProjectPermission, project_id: int, assign_user_id:int, current_user_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    match permission_kind:
        case ProjectPermission.READ:
            check_project_manage_read_permission(project_id, current_user_id, session)
        case ProjectPermission.UPDATE:
            check_project_manage_update_permission(project_id, current_user_id, session)
        case ProjectPermission.DELETE:
            check_project_manage_delete_permission(project_id, current_user_id, session)
        case ProjectPermission.MANAGE_READ | ProjectPermission.MANAGE_UPDATE | ProjectPermission.MANAGE_DELETE:
            check_project_owner_permission(project_id, current_user_id, session)

    assign_user=session.get(User, assign_user_id)
    if not assign_user:
        raise HTTPException(status_code=404, detail="User not found")
    link = session.exec(select(ProjectUserLink).where(ProjectUserLink.user_id == assign_user_id,
                                                      ProjectUserLink.project_id == project_id)).first()
    if not link:
        link = ProjectUserLink(project_id=project_id, user_id=assign_user_id,permission=[])
        session.add(link)
    match permission_kind:
        case ProjectPermission.READ:
            if ProjectPermission.READ in link.permission:
                return {"detail": "Permission already read"}
            link.permission.append(ProjectPermission.READ)
        case ProjectPermission.UPDATE:
            if ProjectPermission.UPDATE in link.permission:
                return {"detail": "Permission already update"}
            link.permission.append(ProjectPermission.UPDATE)
        case ProjectPermission.DELETE:
            if ProjectPermission.DELETE in link.permission:
                return {"detail": "Permission already deleted"}
            link.permission.append(ProjectPermission.DELETE)
        case ProjectPermission.MANAGE_READ:
            if ProjectPermission.MANAGE_READ in link.permission:
                return {"detail": "Permission already read"}
            link.permission.append(ProjectPermission.MANAGE_READ)
        case ProjectPermission.MANAGE_UPDATE:
            if ProjectPermission.MANAGE_UPDATE in link.permission:
                return {"detail": "Permission already updated"}
            link.permission.append(ProjectPermission.MANAGE_UPDATE)
        case ProjectPermission.MANAGE_DELETE:
            if ProjectPermission.MANAGE_DELETE in link.permission:
                return {"detail": "Permission already deleted"}
            link.permission.append(ProjectPermission.MANAGE_DELETE)

    session.commit()
    session.refresh(link)
    return {"detail": "Project assigned"}

@app.post("/projects/{project_id}/permission/read", tags=["projects"])
def read_project_permission(project_id: int,assign_user_id:int, session: Session = Depends(get_session),current_user_id=Depends(get_user_id_from_token)):
    return project_permission_give(ProjectPermission.READ, project_id, assign_user_id, current_user_id, session)

@app.post("/projects/{project_id}/permission/update", tags=["projects"])
def update_project_permission(project_id: int,assign_user_id:int, session: Session = Depends(get_session),current_user_id=Depends(get_user_id_from_token)):
    return project_permission_give(ProjectPermission.UPDATE, project_id, assign_user_id, current_user_id, session)

@app.post("/projects/{project_id}/permission/delete", tags=["projects"])
def delete_project_permission(project_id: int,assign_user_id:int, session: Session = Depends(get_session),current_user_id=Depends(get_user_id_from_token)):
    return project_permission_give(ProjectPermission.DELETE, project_id, assign_user_id, current_user_id, session)

@app.post("/projects/{project_id}/permission/manage_read", tags=["projects"])
def manage_read_project_permission(project_id: int, assign_user_id: int, session: Session = Depends(get_session),current_user_id=Depends(get_user_id_from_token)):
    return project_permission_give(ProjectPermission.MANAGE_READ, project_id, assign_user_id, current_user_id, session)

@app.post("/projects/{project_id}/permission/manage_update", tags=["projects"])
def manage_update_project_permission(project_id: int, assign_user_id: int, session: Session = Depends(get_session),current_user_id=Depends(get_user_id_from_token)):
    return project_permission_give(ProjectPermission.MANAGE_UPDATE, project_id, assign_user_id, current_user_id, session)

@app.post("/projects/{project_id}/permission/manage_delete", tags=["projects"])
def manage_delete_project_permission(project_id: int, assign_user_id: int, session: Session = Depends(get_session),current_user_id=Depends(get_user_id_from_token)):
    return project_permission_give(ProjectPermission.MANAGE_DELETE, project_id, assign_user_id, current_user_id, session)

def project_permission_deprivation(permission_kind:ProjectPermission, project_id: int, assign_user_id:int, current_user_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    match permission_kind:
        case ProjectPermission.READ:
            check_project_manage_read_permission(project_id, current_user_id, session)
        case ProjectPermission.UPDATE:
            check_project_manage_update_permission(project_id, current_user_id, session)
        case ProjectPermission.DELETE:
            check_project_manage_delete_permission(project_id, current_user_id, session)
        case ProjectPermission.MANAGE_READ | ProjectPermission.MANAGE_UPDATE | ProjectPermission.MANAGE_DELETE:
            check_project_owner_permission(project_id, current_user_id, session)

    assign_user=session.get(User, assign_user_id)
    if not assign_user:
        raise HTTPException(status_code=404, detail="User not found")
    link = session.exec(select(ProjectUserLink).where(ProjectUserLink.user_id == assign_user_id,
                                                      ProjectUserLink.project_id == project_id)).first()
    if not link:
        raise HTTPException(status_code=404, detail="User does not have permission for this project")

    if permission_kind not in link.permission:
        return {"detail": "User does not have this permission"}

    link.permission.remove(permission_kind)

    session.commit()
    session.refresh(link)
    return {"detail": "Permission removed"}

@app.delete("/projects/{project_id}/permission/read", tags=["projects"])
def read_project_permission_deprivation(project_id: int,assign_user_id:int, session: Session = Depends(get_session),current_user_id=Depends(get_user_id_from_token)):
    return project_permission_deprivation(ProjectPermission.READ, project_id, assign_user_id, current_user_id, session)

@app.delete("/projects/{project_id}/permission/update", tags=["projects"])
def update_project_permission_deprivation(project_id: int,assign_user_id:int, session: Session = Depends(get_session),current_user_id=Depends(get_user_id_from_token)):
    return project_permission_deprivation(ProjectPermission.UPDATE, project_id, assign_user_id, current_user_id, session)

@app.delete("/projects/{project_id}/permission/delete", tags=["projects"])
def delete_project_permission_deprivation(project_id: int,assign_user_id:int, session: Session = Depends(get_session),current_user_id=Depends(get_user_id_from_token)):
    return project_permission_deprivation(ProjectPermission.DELETE, project_id, assign_user_id, current_user_id, session)


@app.delete("/projects/{project_id}/permission/manage_read", tags=["projects"])
def manage_read_project_permission_deprivation(project_id: int, assign_user_id: int, session: Session = Depends(get_session),current_user_id=Depends(get_user_id_from_token)):
    return project_permission_deprivation(ProjectPermission.MANAGE_READ, project_id, assign_user_id, current_user_id, session)

@app.delete("/projects/{project_id}/permission/manage_update", tags=["projects"])
def manage_update_project_permission_deprivation(project_id: int, assign_user_id: int, session: Session = Depends(get_session),current_user_id=Depends(get_user_id_from_token)):
    return project_permission_deprivation(ProjectPermission.MANAGE_UPDATE, project_id, assign_user_id, current_user_id, session)

@app.delete("/projects/{project_id}/permission/manage_delete", tags=["projects"])
def manage_delete_project_permission_deprivation(project_id: int, assign_user_id: int, session: Session = Depends(get_session),current_user_id=Depends(get_user_id_from_token)):
    return project_permission_deprivation(ProjectPermission.MANAGE_DELETE, project_id, assign_user_id, current_user_id, session)



@app.post("/projects/{project_id}/memos", response_model=MemoRead,tags=["memos"])
def create_project_memo(
    project_id: int, memo: MemoCreate, session: Session = Depends(get_session), current_user_id=Depends(get_user_id_from_token)
):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    check_project_write_permission(project_id, current_user_id, session)
    memo_data = memo.model_dump()
    memo_data["project_id"] = project_id
    memo_data["user_id"] = current_user_id

    memo_obj = Memo(**memo_data)

    session.add(memo_obj)
    session.commit()
    session.refresh(memo_obj)

    return memo_obj


@app.put("/memos/{memo_id}", response_model=MemoRead, tags=["memos"])
def update_project_memo(
    memo_id: int, new_memo: MemoUpdate, session: Session = Depends(get_session), current_user_id=Depends(get_user_id_from_token)
):
    old_memo = session.get(Memo, memo_id)
    if not old_memo:
        raise HTTPException(status_code=404, detail="Memo not found")
    check_project_write_permission(old_memo.project_id, current_user_id, session)
    update_data = new_memo.model_dump(exclude_unset=True)
    old_memo.sqlmodel_update(update_data)
    session.add(old_memo)
    session.commit()
    session.refresh(old_memo)
    return old_memo

@app.get("/projects/{project_id}/memos", response_model=List[MemoRead], tags=["memos"])
def read_project_memos(project_id: int, session: Session = Depends(get_session), current_user_id=Depends(get_user_id_from_token)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    check_project_read_permission(project_id, current_user_id, session)
    statement = select(Memo).where(Memo.project_id == project_id)
    memos = session.exec(statement).all()
    return memos


@app.get("/memos/{memo_id}", response_model=MemoRead, tags=["memos"])
def read_project_memo(memo_id: int, session: Session = Depends(get_session), current_user_id=Depends(get_user_id_from_token)):
    memo = session.get(Memo, memo_id)
    if not memo:
        raise HTTPException(status_code=404, detail="Memo not found")
    check_project_read_permission(memo.project_id, current_user_id, session)
    return memo


@app.delete("/memos/{memo_id}", tags=["memos"])
def delete_project_memo(memo_id: int, session: Session = Depends(get_session),current_user_id=Depends(get_user_id_from_token)):
    memo = session.get(Memo, memo_id)
    if not memo:
        raise HTTPException(status_code=404, detail="Memo not found")
    check_project_write_permission(memo.project_id, current_user_id, session)
    session.delete(memo)
    session.commit()
    return {"detail": "Memo deleted"}

@app.post("/memos/{memo_id}/chats", response_model=ChatRead, tags=["chats"])
def create_project_memo_chat(
    memo_id: int, chat_text: str, session: Session = Depends(get_session), current_user_id=Depends(get_user_id_from_token)
):
    memo = session.get(Memo, memo_id)
    if not memo:
        raise HTTPException(status_code=404, detail="Memo not found")
    check_project_write_permission(memo.project_id, current_user_id, session)

    chat_data = {"text": chat_text, "memo_id": memo_id, "user_id": current_user_id}
    chat_obj = Chat(**chat_data)

    session.add(chat_obj)
    session.commit()
    session.refresh(chat_obj)

    return chat_obj


@app.get("/memos/{memo_id}/chats", response_model=List[ChatRead], tags=["chats"])
def read_project_memo_chats(memo_id: int, session: Session = Depends(get_session), current_user_id=Depends(get_user_id_from_token)):
    memo = session.get(Memo, memo_id)
    if not memo:
        raise HTTPException(status_code=404, detail="Memo not found")
    check_project_read_permission(memo.project_id, current_user_id, session)

    statement = select(Chat).where(Chat.memo_id == memo_id)
    chats = session.exec(statement).all()

    return chats


@app.put("/chats/{chat_id}", response_model=ChatRead, tags=["chats"])
def update_project_memo_chat(
    chat_id: int, new_chat: ChatUpdate, session: Session = Depends(get_session), current_user_id=Depends(get_user_id_from_token)
):
    chat = session.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    check_project_write_permission(chat.memo.project_id, current_user_id, session)

    chat.text = new_chat.text
    session.add(chat)
    session.commit()
    session.refresh(chat)

    return chat

@app.delete("/chats/{chat_id}", tags=["chats"])
def delete_project_memo_chat(chat_id: int, session: Session = Depends(get_session), current_user_id=Depends(get_user_id_from_token)):
    chat = session.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    check_project_write_permission(chat.memo.project_id, current_user_id, session)

    session.delete(chat)
    session.commit()

    return {"detail": "Chat deleted"}