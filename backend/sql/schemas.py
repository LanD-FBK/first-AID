from typing import Union

from pydantic import BaseModel


class Option(BaseModel):
    id: str
    value: Union[str, None] = None

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str
    username: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True