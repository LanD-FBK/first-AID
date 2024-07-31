from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config.settings import settings

DB_ENGINE = settings.DB_ENGINE

connect_args = {}
if DB_ENGINE.startswith("sqlite"):
    # See: https://fastapi.tiangolo.com/tutorial/sql-databases/
    connect_args = {"check_same_thread": False}
engine = create_engine(DB_ENGINE, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

