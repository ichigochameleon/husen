from fastapi import HTTPException
from sqlmodel import Session, select
from back.db.db_base import ProjectUserLink

def check_project_permission(project_id: int, user_id: int, session: Session):
    link = session.exec(
        select(ProjectUserLink).where(
            ProjectUserLink.project_id == project_id,
            ProjectUserLink.user_id == user_id
        )
    ).first()

    if not link:
        raise HTTPException(status_code=403, detail="You do not have permission to access this project.")

    return link

def check_project_read_permission(project_id: int, user_id: int, session: Session):
    link = check_project_permission(project_id, user_id, session)
    return link

def check_project_write_permission(project_id: int, user_id: int, session: Session):
    link = check_project_permission(project_id, user_id, session)

    if link.role not in ("owner", "member"):
        raise HTTPException(status_code=403, detail="You do not have write permission for this project.")

    return link

def check_project_delete_permission(project_id: int, user_id: int, session: Session):
    link = check_project_permission(project_id, user_id, session)

    if link.role != "owner":
        raise HTTPException(status_code=403, detail="You do not have delete permission for this project.")

    return link