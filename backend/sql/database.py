from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import create_engine, Session

from config.settings import settings

DB_ENGINE = settings.DB_ENGINE

connect_args = {}
if DB_ENGINE.startswith("sqlite"):
    # See: https://fastapi.tiangolo.com/tutorial/sql-databases/
    connect_args = {"check_same_thread": False}
engine = create_engine(DB_ENGINE, connect_args=connect_args)

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
