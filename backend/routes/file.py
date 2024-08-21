import hashlib
import os
import shutil
from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlmodel import Session

import sql.crud as crud
from routes.login import get_current_user
from sql.database import get_db
from sql.dboptions import getOption
from sql.models import FileCreate, File
from sql.models import Project

router = APIRouter()

@router.post("/", status_code=204)
async def call_project_add_files(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[bool, Depends(get_current_user)],
        project_id: int,
        files: List[UploadFile]
    ):
    check_manage_project(db, project_id, user)
    db_project = crud.get_object_by_id(db, obj_id=project_id, obj_type=Project)

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
