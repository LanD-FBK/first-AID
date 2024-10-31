from datetime import datetime, timedelta, timezone
from typing import Annotated, Union

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from sqlmodel import Session, select

import sql.crud as crud
from sql.database import get_db
from sql.dboptions import getOption
from sql.models import User, ProjectUserLink

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

incorrect_login_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)

inactive_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="User is not active",
    headers={"WWW-Authenticate": "Bearer"},
)

deleted_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="User has been deleted",
    headers={"WWW-Authenticate": "Bearer"},
)

only_admin_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Only admin can do that",
    headers={"WWW-Authenticate": "Bearer"},
)


class Token(BaseModel):
    access_token: str
    token_type: str
    is_admin: bool
    is_active: bool
    project_manager: set


class TokenData(BaseModel):
    username: Union[str, None] = None


def authenticate_user(db, username: str, password: str):
    user = crud.get_user_by_username_or_email(db, username)
    if not user:
        return False
    if not crud.verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    secret_key = getOption("SECRET_KEY")
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=getOption("JWT_ALGORITHM"))
    return encoded_jwt


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Session = Depends(get_db),
):
    try:
        secret_key = getOption("SECRET_KEY")
        payload = jwt.decode(token, secret_key, algorithms=[getOption("JWT_ALGORITHM")])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = crud.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise inactive_exception
    if user.is_deleted:
        raise deleted_exception
    return user


async def user_must_be_admin(
        current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.is_admin:
        raise only_admin_exception
    return current_user.is_admin


@router.post("/token")
async def call_login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Session = Depends(get_db),
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise incorrect_login_exception
    if not user.is_active:
        raise inactive_exception
    access_token_expires = timedelta(minutes=getOption("ACCESS_TOKEN_EXPIRE_MINUTES", ret_type=int))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    stmt = select(ProjectUserLink).where(ProjectUserLink.user_id == user.id, ProjectUserLink.is_project_admin == True)
    results = db.exec(stmt).all()
    project_manager = set()
    for result in results:
        project_manager.add(result.project_id)
    return Token(access_token=access_token, token_type="bearer", is_admin=user.is_admin, is_active=user.is_active,
                 project_manager=project_manager)
