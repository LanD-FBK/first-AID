from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from routes.login import get_current_user
from routes.project import check_manage_project
from sql.crud import get_object_by_id
from sql.database import get_db
from sql.models import User, AnnotationCreate, Task, Annotation, AnnotationOut, AnnotationOutSimple, AnnotationEdit

router = APIRouter()


@router.get("/")
async def call_get_annotations(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[User, Depends(get_current_user)],
        project_id: int,
        task_id: int
) -> List[AnnotationOutSimple]:
    # see comments below
    stmt = select(Annotation).where(Annotation.task_id == task_id)
    results = db.exec(stmt).all()
    return results


@router.post("/")
async def call_create_annotation(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[User, Depends(get_current_user)],
        project_id: int,
        task_id: int,
        annotation: AnnotationCreate,
) -> AnnotationOut:
    # TODO: check task-user-project compatibility
    # the check_manage_project function is not mandatory
    # db_project = check_manage_project(db, project_id, user)
    db_task = get_object_by_id(db, task_id, Task)
    if not db_task:
        raise HTTPException(status_code=400, detail=f"Task {task_id} does not exist")
    if db_task.project_id != project_id:
        raise HTTPException(status_code=400, detail=f"Inconsistence between task {task_id} and project {project_id}")

    if not annotation.comment:
        raise HTTPException(status_code=400, detail=f"Please provide a comment for annotation")
    # TODO: check JSON

    if annotation.parent != 0:
        db_parent = get_object_by_id(db, annotation.parent, Annotation)
        if db_parent.task_id != task_id:
            raise HTTPException(status_code=400,
                                detail=f"Parent annotation {db_parent.task_id} does not belong to task {task_id}")

    db_annotation = Annotation.model_validate(annotation, update={"task_id": task_id, "user_id": user.id})
    db_annotation.user = user

    db.add(db_annotation)
    db.commit()
    db.refresh(db_annotation)
    return db_annotation


@router.get("/{annotation_id}")
async def call_get_annotation(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[User, Depends(get_current_user)],
        project_id: int,
        task_id: int,
        annotation_id: int
) -> AnnotationOut:
    # see comments above
    db_task = get_object_by_id(db, task_id, Task)
    if not db_task:
        raise HTTPException(status_code=400, detail=f"Task {task_id} does not exist")
    if db_task.project_id != project_id:
        raise HTTPException(status_code=400, detail=f"Inconsistence between task {task_id} and project {project_id}")

    db_annotation = get_object_by_id(db, annotation_id, Annotation)
    return db_annotation


@router.patch("/{annotation_id}")
async def call_edit_annotation(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[User, Depends(get_current_user)],
        project_id: int,
        task_id: int,
        annotation_id: int,
        annotation: AnnotationEdit,
) -> AnnotationOut:
    # see comments above
    db_annotation = get_object_by_id(db, annotation_id, Annotation)

    annotation_data = annotation.model_dump(exclude_unset=True)
    db_annotation.sqlmodel_update(annotation_data)
    db.add(db_annotation)
    db.commit()
    db.refresh(db_annotation)

    return db_annotation
