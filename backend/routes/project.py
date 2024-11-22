from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

import sql.crud as crud
from routes.common import ListCommons
from routes.login import get_current_user, user_must_be_admin
from sql.crud import get_object_by_id
from sql.database import get_db
from sql.models import ProjectOutputWithUsers, ProjectCreate, Project, ProjectUserLink, ProjectOutputWithEverything, \
    Task, TaskUserLink
from sql.models import User

router = APIRouter()


def get_users_from_project(db: Session, project: ProjectCreate):
    if project.users_list is None or project.users_manage is None:
        return None
    if len(project.users_list) != len(project.users_manage):
        raise HTTPException(status_code=400, detail="Arrays 'users_list' and 'users_manage' do not match")
    users = []
    for i in range(len(project.users_list)):
        user = crud.get_user_by_id(db, project.users_list[i])
        if not user:
            raise HTTPException(status_code=400, detail=f"User {project.users_list[i]} not found")
        user_is_admin = project.users_manage[i]
        users.append((user, user_is_admin))
    return users


def check_manage_project(db: Session, project_id: int, user: User, return_bool=False):
    db_obj = get_object_by_id(db, project_id, Project)
    if not db_obj:
        raise HTTPException(status_code=400, detail=f"Project {project_id} does not exist")

    # If admin is logged, it's ok even if the project is not active ...
    if user.is_admin:
        if return_bool:
            return (db_obj, True)
        else:
            return db_obj

    # ... otherwise it's not possible to do anything on it
    if not db_obj.is_active:
        raise HTTPException(status_code=400, detail=f"Project {project_id} is not active")

    ret = crud.get_existing_elements(db, ProjectUserLink) \
        .where(ProjectUserLink.project_id == project_id) \
        .where(ProjectUserLink.user_id == user.id).first()

    if not ret:
        raise HTTPException(status_code=400, detail=f"User {user.username} is not included in {project_id}")

    if return_bool:
        return (db_obj, ret.is_project_admin)
    else:
        if not ret.is_project_admin:
            raise HTTPException(status_code=400, detail=f"User {user.username} cannot manage project {project_id}")

        return db_obj


@router.get("/")
async def call_list_projects(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[User, Depends(get_current_user)],
        commons: Annotated[ListCommons, Depends(ListCommons)],
) -> list[ProjectOutputWithUsers]:
    projects = crud.get_projects(db, skip=commons.skip, limit=commons.limit, user=user)
    return projects


@router.post("/", status_code=201)
async def call_create_project(
        db: Annotated[Session, Depends(get_db)],
        is_admin: Annotated[bool, Depends(user_must_be_admin)],
        project: ProjectCreate,
) -> ProjectOutputWithUsers:
    try:
        users = get_users_from_project(db, project)
        return crud.create_project(db=db, project=project, users=users)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}")
async def call_get_project(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[bool, Depends(get_current_user)],
        project_id: int,
# ):
) -> ProjectOutputWithEverything:
    (db_project, is_manager) = check_manage_project(db, project_id, user, True)
    if is_manager:
        return db_project
    else:
        d = db_project.dict()
        stmt = select(Task, TaskUserLink).where(Task.id == TaskUserLink.task_id, Task.project_id == project_id, TaskUserLink.user_id == user.id)
        results = db.exec(stmt).all()
        d['tasks'] = []
        for result in results:
            d['tasks'].append(result[0])
        return d


@router.patch("/{project_id}/edit")
async def call_edit_project(
        db: Annotated[Session, Depends(get_db)],
        is_admin: Annotated[bool, Depends(user_must_be_admin)],
        project: ProjectCreate,
        project_id: int,
) -> ProjectOutputWithUsers:
    db_project = crud.get_object_by_id(db, obj_id=project_id, obj_type=Project)
    if not db_project:
        raise HTTPException(status_code=400, detail=f"Project {project_id} does not exist")
    try:
        users = get_users_from_project(db, project)
        return crud.edit_project(db=db, db_project=db_project, project=project, users=users)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{project_id}/assignuser")
async def call_assign_user(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[bool, Depends(get_current_user)],
        user_id: int,
        user_manage: bool,
        project_id: int,
) -> ProjectOutputWithUsers:
    check_manage_project(db, project_id, user)
    if user_manage and not user.is_admin:
        raise HTTPException(status_code=400, detail=f"Only admin can edit project managers")
    return crud.assign_user_to_project(db, project_id, user_id, user_manage)


@router.delete("/{project_id}/revokeuser")
async def call_revoke_user(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[bool, Depends(get_current_user)],
        user_id: int,
        project_id: int,
) -> ProjectOutputWithUsers:
    check_manage_project(db, project_id, user)
    # db_user = crud.get_object_by_id(db, user_id, User)
    is_user_manager = crud.get_existing_elements(db, ProjectUserLink) \
        .where(ProjectUserLink.project_id == project_id) \
        .where(ProjectUserLink.user_id == user_id) \
        .where(ProjectUserLink.is_project_admin == True).first()
    if is_user_manager and not user.is_admin:
        raise HTTPException(status_code=400, detail=f"Only admin can edit project managers")
    return crud.revoke_user_from_project(db, project_id, user_id)


@router.delete("/{project_id}", status_code=204)
async def call_delete_project(
        db: Annotated[Session, Depends(get_db)],
        is_admin: Annotated[bool, Depends(user_must_be_admin)],
        project_id: int,
):
    db_project = crud.get_object_by_id(db, obj_id=project_id, obj_type=Project)
    if not db_project:
        raise HTTPException(status_code=400, detail=f"Project {project_id} does not exist")
    crud.delete_project(db=db, db_project=db_project)
    # try:
    #     crud.delete_project(db=db, db_project=db_project)
    # except Exception as e:
    #     raise HTTPException(status_code=400, detail=str(e))
