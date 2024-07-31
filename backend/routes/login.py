from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated, Union
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError

from sql.crud import verify_password, get_password_hash, get_user_by_username_or_email, get_user_by_username
from sql.dboptions import getOption
from sql.database import get_db
from sql.models import User
import sql.schemas as schemas

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


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None


def authenticate_user(db, username: str, password: str):
    user = get_user_by_username_or_email(db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
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
    user = get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user

async def user_is_admin(
    current_user: Annotated[schemas.User, Depends(get_current_user)],
):
    return current_user.is_admin
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    # return current_user


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise incorrect_login_exception
    access_token_expires = timedelta(minutes=getOption("ACCESS_TOKEN_EXPIRE_MINUTES", ret_type=int))
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

