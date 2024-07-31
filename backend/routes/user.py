from fastapi import APIRouter, Depends, Query
from typing import Annotated
from sqlalchemy.orm import Session

import sql.crud as crud
import sql.schemas as schemas
from sql.database import get_db

from routes.login import oauth2_scheme, user_is_admin
from routes.common import ListCommons

router = APIRouter()

@router.get("/")
async def read_users(
        is_admin: Annotated[bool, Depends(user_is_admin)],
        db: Annotated[Session, Depends(get_db)],
        commons: Annotated[dict, Depends(ListCommons)],
    ) -> list[schemas.User]:
    users = crud.get_users(db, skip=commons.skip, limit=commons.limit)
    return users

@router.post("/create")
async def create_user(
        is_admin: Annotated[bool, Depends(user_is_admin)],
        db: Annotated[Session, Depends(get_db)],
        user: schemas.UserCreate,
    ) -> schemas.User:
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)
    
# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user
