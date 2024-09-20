import enum
from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic.v1 import BaseModel
from sqlalchemy import Column, JSON, Enum
from sqlalchemy.orm import ORMExecuteState, with_loader_criteria
from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship
from sqlmodel import Session, col

"""

Many-to-many with additional fields
https://sqlmodel.tiangolo.com/tutorial/many-to-many/link-with-extra-fields/

LEFT OUTER
https://sqlmodel.tiangolo.com/tutorial/connect/read-connected-data/

Models with relationship
https://sqlmodel.tiangolo.com/tutorial/fastapi/relationships/

Document responses
https://fastapi.tiangolo.com/advanced/additional-responses/

"""


### Templates

class TimestampModel(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})


class DeletedModel(SQLModel):
    is_deleted: bool = Field(default=False)
    model_config = ConfigDict(populate_by_name=True)

    @classmethod
    def make_where_criteria(cls) -> sa.BinaryExpression[bool]:
        return col(getattr(cls, "is_deleted")) == False


### Tables - Option

class Option(SQLModel, table=True):
    __tablename__: str = "option"

    id: str = Field(max_length=50, default=None, primary_key=True)
    value: str


### Tables - ProjectUserLink

class ProjectUserLinkOutput(SQLModel):
    project_id: Optional[int] = Field(default=None, foreign_key="project.id", primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)
    is_project_admin: bool = False


class ProjectUserLinkOutputWithUser(ProjectUserLinkOutput):
    user: "UserOutput"


class ProjectUserLink(ProjectUserLinkOutput, DeletedModel, table=True):
    __tablename__: str = "project_user"

    project: "Project" = Relationship(back_populates="users")
    user: "User" = Relationship(back_populates="projects")


### Tables - User

class UserBase(SQLModel):
    __table_args__ = (UniqueConstraint("username"), UniqueConstraint("email"),)

    email: EmailStr = Field(index=True)
    username: str = Field(index=True)


class UserOutput(UserBase):
    is_active: bool = True
    is_admin: bool = False
    id: Optional[int] = Field(default=None, primary_key=True)


class UserCreate(UserBase):
    password: str = Field(default=None)


class User(UserOutput, TimestampModel, DeletedModel, table=True):
    __tablename__: str = "user"
    password: str = Field(default=None)
    projects: list['ProjectUserLink'] = Relationship(back_populates="user")
    tasks: list["TaskUserLink"] = Relationship(back_populates="user")


### Tables - Project

class ProjectBase(SQLModel):
    name: str = Field(default=None)
    is_active: bool = True


class ProjectCreate(ProjectBase):
    users_list: list[int] = []
    users_manage: list[bool] = []


class ProjectOutput(ProjectBase):
    id: Optional[int] = Field(default=None, primary_key=True)


class Project(ProjectOutput, TimestampModel, DeletedModel, table=True):
    __tablename__: str = "project"
    users: list['ProjectUserLink'] = Relationship(back_populates="project")
    files: list['File'] = Relationship(back_populates="project")
    tasks: list['Task'] = Relationship(back_populates="project")

    """
    This code add a SQLAlchemy rule that checks the is_deleted field.
    It has been replaced by the solutions below.
    """

    # users: list['ProjectUserLink'] = Relationship(
    #     back_populates="project",
    #     sa_relationship=relationship(
    #         "ProjectUserLink",
    #         secondary="user",
    #         primaryjoin="ProjectUserLink.project_id == Project.id",
    #         secondaryjoin="and_(ProjectUserLink.user_id == User.id, User.is_deleted == False)",
    #         back_populates="project",
    #     )
    # )


class ProjectOutputWithUsers(ProjectOutput):
    users: list['ProjectUserLinkOutputWithUser'] = []


class ProjectOutputWithEverything(ProjectOutput):
    files: list['FileOutput'] = []
    users: list['ProjectUserLinkOutputWithUser'] = []
    tasks: list['TaskOutSimple'] = []


### Tables - Project

class FileBase(SQLModel):
    name: str
    size: int


class FileCreate(FileBase):
    filename: str
    project_id: int = Field(foreign_key="project.id")


class FileOutput(FileBase):
    id: int


class File(FileCreate, TimestampModel, DeletedModel, table=True):
    __tablename__: str = "file"
    id: Optional[int] = Field(default=None, primary_key=True)
    project: Project = Relationship(back_populates="files")
    tasks: list["TaskFileLink"] = Relationship(back_populates="file")


### Tables - Task

class TaskStartType(str, enum.Enum):
    empty = "empty"
    pre_compiled = "pre_compiled"


class TaskInsideType(str, enum.Enum):
    clean = "clean"
    choice = "choice"


class TaskBase(SQLModel):
    name: str
    start_type: TaskStartType = Field(sa_column=Column(Enum(TaskStartType)))
    inside_type: TaskInsideType = Field(sa_column=Column(Enum(TaskInsideType)))
    language: str = "it"
    is_active: bool = True
    meta: dict = Field(default_factory=dict, sa_column=Column(JSON))


class TaskOutSimple(SQLModel):
    name: str
    is_active: bool
    id: int


class TaskOut(TaskBase):
    users: list["TaskUserLinkOutputWithUser"] = []
    files: list["TaskFileLinkOutputWithFile"] = []
    actors: list["ActorCreate"] = []


class TaskRequest(TaskBase):
    users_list: list[int] = []
    files_list: list[int] = []


class Task(TaskBase, TimestampModel, DeletedModel, table=True):
    __tablename__: str = "task"
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    project: Project = Relationship(back_populates="tasks")
    actors: list["Actor"] = Relationship(back_populates="task")
    users: list["TaskUserLink"] = Relationship(back_populates="task")
    files: list["TaskFileLink"] = Relationship(back_populates="task")


class ActorCreate(SQLModel):
    # TODO: check format of label
    label: str
    name: str


class Actor(ActorCreate, TimestampModel, DeletedModel, table=True):
    __tablename__: str = "actor"
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    task: Task = Relationship(back_populates="actors")


class TaskCreate(TaskBase):
    # actors_list: list[ActorCreate] = [ActorCreate(label="label", name="Actor name")]
    actors_list: list[ActorCreate] = []
    users_list: list[int] = []
    files_list: list[int] = []


### Tables - TaskUserLink

class TaskUserLinkOutput(SQLModel):
    task_id: Optional[int] = Field(default=None, foreign_key="task.id", primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", primary_key=True)


class TaskUserLinkOutputWithUser(TaskUserLinkOutput):
    user: "UserOutput"


class TaskUserLink(TaskUserLinkOutput, DeletedModel, table=True):
    __tablename__: str = "task_user"

    task: "Task" = Relationship(back_populates="users")
    user: "User" = Relationship(back_populates="tasks")


### Tables - TaskUserLink

class TaskFileLinkOutput(SQLModel):
    task_id: Optional[int] = Field(default=None, foreign_key="task.id", primary_key=True)
    file_id: Optional[int] = Field(default=None, foreign_key="file.id", primary_key=True)


class TaskFileLinkOutputWithFile(TaskFileLinkOutput):
    file: "FileOutput"


class TaskFileLink(TaskFileLinkOutput, DeletedModel, table=True):
    __tablename__: str = "task_file"

    task: "Task" = Relationship(back_populates="files")
    file: "File" = Relationship(back_populates="tasks")


"""
# Soft deletion callback

This function intercept all SQL queries and add a WHERE condition
checking that is_deleted is false.

See here:
https://github.com/sqlalchemy/sqlalchemy/discussions/10517
https://github.com/fastapi/sqlmodel/discussions/989
https://docs.sqlalchemy.org/en/20/orm/session_events.html
https://docs.sqlalchemy.org/en/20/_modules/examples/extending_query/filter_public.html
"""


@sa.event.listens_for(Session, 'do_orm_execute')
def _do_orm_execute(orm_execute_state: ORMExecuteState) -> None:
    if not (
            orm_execute_state.is_select
            and not orm_execute_state.is_column_load
            and not orm_execute_state.is_relationship_load
    ):
        return

    orm_execute_state.statement = orm_execute_state.statement.options(
        with_loader_criteria(
            DeletedModel,
            lambda cls: cls.make_where_criteria() if hasattr(cls, 'is_deleted') else None,
            include_aliases=True,
            propagate_to_loaders=True,
        ),
    )
