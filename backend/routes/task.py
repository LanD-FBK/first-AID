from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from routes.login import get_current_user
from routes.project import check_manage_project
from sql.crud import get_object_by_id
from sql.database import get_db
from sql.models import Task, User, TaskOut, TaskCreate, TaskUserLink, File, TaskFileLink

router = APIRouter()


@router.post("/", status_code=201)
async def call_create_task(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[User, Depends(get_current_user)],
        project_id: int,
        task: TaskCreate,
) -> TaskOut:
    db_project = check_manage_project(db, project_id, user)
    allowed_files = set()
    files = []
    for file in db_project.files:
        allowed_files.add(file.id)
    for fid in task.files_list:
        if fid not in allowed_files:
            raise HTTPException(status_code=400, detail=f"File {fid} is not allowed in project {project_id}")
        files.append(fid)
    allowed_users = set()
    users = []
    for user in db_project.users:
        allowed_users.add(user.user_id)
    for uid in task.users_list:
        if uid not in allowed_users:
            raise HTTPException(status_code=400, detail=f"User {uid} is not allowed in project {project_id}")
        users.append(uid)

    print(task.actors_list)
    # TODO: check and insert actors

    db_task = Task.model_validate(task, update={"project_id": project_id})
    db.add(db_task)
    if users is not None:
        for user in users:
            db_user = get_object_by_id(db, user, User)
            db_obj = TaskUserLink(task=db_task, user=db_user)
            db.add(db_obj)
    if files is not None:
        for file in files:
            db_file = get_object_by_id(db, file, File)
            db_obj = TaskFileLink(task=db_task, file=db_file)
            db.add(db_obj)

    db.commit()
    db.refresh(db_task)
    return db_task

    # db_user = crud.get_user_by_email(db, email=user.email)
    # if db_user:
    #     raise HTTPException(status_code=400, detail="Email already registered")
    # try:
    #     return crud.create_user(db=db, user=user)
    # except Exception as e:
    #     raise HTTPException(status_code=400, detail=str(e))


@router.get("/{task_id}")
async def call_task_info(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[User, Depends(get_current_user)],
        project_id: int,
        task_id: int,
) -> TaskOut:
    db_task = get_object_by_id(db, task_id, Task)
    if db_task.project_id != project_id:
        raise HTTPException(status_code=400, detail=f"Task {task_id} does not belong to project {project_id}")
    db_project = check_manage_project(db, db_task.project_id, user)
    return db_task
