from fastapi import HTTPException
from sqlmodel import Session, select
from back.db.db_base import ProjectUserLink,ProjectPermission,ProjectExit,Project

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
    project=session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found.")

    if project.project_exist==ProjectExit.PUBLIC:
        return True

    link = check_project_permission(project_id, user_id, session)

    if ProjectPermission.READ in link.permission:
        return True

    else:
        raise HTTPException(status_code=403, detail="You do not have read permission for this project.")

def check_project_write_permission(project_id: int, user_id: int, session: Session):
    link = check_project_permission(project_id, user_id, session)

    if ProjectPermission.UPDATE in link.permission:
        return True
    raise HTTPException(status_code=403, detail="You do not have write permission for this project.")

def check_project_delete_permission(project_id: int, user_id: int, session: Session):
    link = check_project_permission(project_id, user_id, session)

    if ProjectPermission.DELETE in link.permission:
        return True

    raise HTTPException(status_code=403, detail="You do not have delete permission for this project.")

def check_project_manage_read_permission(project_id: int, user_id: int, session: Session):
    link = check_project_permission(project_id, user_id, session)

    if ProjectPermission.MANAGE_READ in link.permission:
        return True

    raise HTTPException(status_code=403, detail="You do not have manage_read permission for this project.")

def check_project_manage_update_permission(project_id: int, user_id: int, session: Session):
    link = check_project_permission(project_id, user_id, session)
    if ProjectPermission.MANAGE_UPDATE in link.permission:
        return True
    raise HTTPException(status_code=403, detail="You do not have manage_update permission for this project.")

def check_project_manage_delete_permission(project_id: int, user_id: int, session: Session):
    link = check_project_permission(project_id, user_id, session)
    if ProjectPermission.MANAGE_DELETE in link.permission:
        return True
    raise HTTPException(status_code=403, detail="You do not have manage_delete_permission for this project.")

def check_project_owner_permission(project_id: int, user_id: int, session: Session):
    link = check_project_permission(project_id, user_id, session)
    if ProjectPermission.OWNER in link.permission:
        return True
    raise HTTPException(status_code=403, detail="You do not have owner permission for this project.")