from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session

import sql.crud as crud
from routes.common import ListCommons
from routes.login import user_must_be_admin, get_current_user
from sql.database import get_db
from sql.dboptions import getOption
from sql.models import UserOutput, UserCreate, User

router = APIRouter()


@router.get("/")
async def call_read_users(
        db: Annotated[Session, Depends(get_db)],
        is_admin: Annotated[bool, Depends(user_must_be_admin)],
        commons: Annotated[dict, Depends(ListCommons)],
        response: Response
) -> list[UserOutput]:
    users = crud.get_users(db, skip=commons.skip, limit=commons.limit)
    return users


@router.post("/", status_code=201)
async def call_create_user(
        db: Annotated[Session, Depends(get_db)],
        is_admin: Annotated[bool, Depends(user_must_be_admin)],
        user: UserCreate,
) -> UserOutput:
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    try:
        return crud.create_user(db=db, user=user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{user_id}/edit")
async def call_edit_user(
        db: Annotated[Session, Depends(get_db)],
        is_admin: Annotated[bool, Depends(user_must_be_admin)],
        user: UserCreate,
        user_id: int
) -> UserOutput:
    db_user = crud.get_user_by_id(db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=400, detail=f"User with id {user_id} does not exist")
    admin_user = getOption("ADMIN_USER")
    if db_user.username == admin_user:
        if user.username != admin_user:
            raise HTTPException(status_code=400, detail=f"Admin username ({admin_user}) cannot be modified")
    try:
        return crud.edit_user(db=db, db_user=db_user, user=user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me")
async def call_user_info(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[User, Depends(get_current_user)],
) -> UserOutput:
    return user

@router.patch("/me/changepassword", status_code=204)
async def call_change_password(
        db: Annotated[Session, Depends(get_db)],
        user: Annotated[bool, Depends(get_current_user)],
        old_password: str,
        new_password: str
):
    if not crud.verify_password(old_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    crud.change_password(db=db, db_user=user, new_password=new_password)


@router.patch("/{user_id}/changeactivestate")
async def call_change_active_state(
        db: Annotated[Session, Depends(get_db)],
        is_admin: Annotated[bool, Depends(user_must_be_admin)],
        user_id: int,
) -> UserOutput:
    db_user = crud.get_user_by_id(db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=400, detail=f"User with id {user_id} does not exist")
    if db_user.is_admin:
        raise HTTPException(status_code=400, detail=f"You cannot deactiveate an admin")
    try:
        return crud.change_active_state(db=db, db_user=db_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", status_code=204)
async def call_delete(
        db: Annotated[Session, Depends(get_db)],
        is_admin: Annotated[bool, Depends(user_must_be_admin)],
        user_id: int,
):
    db_user = crud.get_user_by_id(db, id=user_id)
    if not db_user:
        raise HTTPException(status_code=400, detail=f"User with id {user_id} does not exist")
    admin_user = getOption("ADMIN_USER")
    username = db_user.username
    if username == admin_user:
        raise HTTPException(status_code=400, detail=f"Admin user ({admin_user}) cannot be deleted")
    # TODO: Check if it is included in a project
    try:
        crud.delete_user(db=db, db_user=db_user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
