import logging

from fastapi import FastAPI
from sqlmodel import SQLModel

from config.start import app_init, get_middleware
from mw import MyMiddleware
from routes import login, user, project, file, task, annotation
from sql.database import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create all tables
SQLModel.metadata.create_all(engine)

app_init()

app = FastAPI(
    middleware=get_middleware(),
    # https://stackoverflow.com/questions/70793174/fastapi-schemahidden-true-not-working-when-trying-to-hide-the-schema-sectio
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)
app.add_middleware(MyMiddleware)

app.include_router(login.router, tags=["Login"])
app.include_router(user.router, tags=["Users"], prefix="/users")
app.include_router(project.router, tags=["Projects"], prefix="/projects")
app.include_router(file.router, tags=["Files"], prefix="/projects/{project_id}/file")
app.include_router(task.router, tags=["Tasks"], prefix="/projects/{project_id}/tasks")

app.include_router(annotation.router, tags=["Annotations"], prefix="/projects/{project_id}/tasks/{task_id}/annotations")
