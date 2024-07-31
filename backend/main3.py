from fastapi import FastAPI
from routes import login, user

from sql.models import Base
from sql.database import engine
from config.start import app_init, get_middleware
from sql.dboptions import getOption

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app_init()

app = FastAPI(middleware=get_middleware())

app.include_router(login.router, tags=["login"])
app.include_router(user.router, tags=["user"], prefix="/users")

