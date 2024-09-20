import hashlib
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse
from sqlmodel import Session

import sql.crud as crud
from routes.login import get_current_user
from routes.project import check_manage_project
from sql.crud import get_object_by_id
from sql.database import get_db
from sql.dboptions import getOption
from sql.models import FileCreate, File, User, FileOutput

router = APIRouter()


@router.get("/")
async def call_project_get_files(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[User, Depends(get_current_user)],
        project_id: int
) -> list[FileOutput]:
    check_manage_project(db, project_id, user)
    files = crud.get_existing_elements(db, File).filter(File.project_id == project_id).all()
    return files


@router.post("/")
async def call_project_add_files(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[User, Depends(get_current_user)],
        project_id: int,
        files: List[UploadFile]
) -> list[FileOutput]:
    check_manage_project(db, project_id, user)
    # db_project = crud.get_object_by_id(db, obj_id=project_id, obj_type=Project)

    files_folder = getOption("SAVE_PATH")
    out_files = []
    try:
        for file in files:
            ts = str(datetime.now().timestamp())
            hash_name = f"{file.filename}-{ts}"
            result = hashlib.md5(hash_name.encode()).hexdigest()
            f = FileCreate(name=file.filename, filename=result, size=file.size, project_id=project_id)
            db_obj = File.model_validate(f)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            save_file = os.path.join(files_folder, result)
            with open(save_file, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            # save files here
            out_files.append(db_obj)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return out_files


@router.delete("/delete", status_code=204)
async def call_project_delete_files(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[User, Depends(get_current_user)],
        project_id: int,
        file_ids: list[int]
):
    check_manage_project(db, project_id, user)
    # TODO: check that the files are not used in any task
    to_delete = []
    for file_id in file_ids:
        db_obj = get_object_by_id(db, file_id, File)
        if db_obj.project_id != project_id:
            raise HTTPException(status_code=400, detail=f"File {file_id} does not belong to project {project_id}")
        if not db_obj:
            raise HTTPException(status_code=400, detail=f"File {file_id} does not exist")
        db_obj.is_deleted = True
        to_delete.append(db_obj)
    for db_obj in to_delete:
        db.add(db_obj)
        db.commit()

@router.get("/{file_id}/content", response_class=PlainTextResponse)
async def call_project_get_file_content(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[User, Depends(get_current_user)],
        project_id: int,
        file_id: int
):
    # TODO: check that the user can view the file
    db_obj = get_object_by_id(db, file_id, File)
    if db_obj.project_id != project_id:
        raise HTTPException(status_code=400, detail=f"File {file_id} does not belong to project {project_id}")
    if not db_obj:
        raise HTTPException(status_code=400, detail=f"File {file_id} does not exist")
    files_folder = getOption("SAVE_PATH")
    file_path = os.path.join(files_folder, db_obj.filename)
    contents = Path(file_path).read_text()

    # with open(save_file, "wb") as buffer:
    #     shutil.copyfileobj(file.file, buffer)
    # # save files here
    # out_files.append(db_obj)
    return contents