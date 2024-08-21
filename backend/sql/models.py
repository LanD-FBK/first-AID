from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from pydantic import ConfigDict
from pydantic import EmailStr
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
    __table_args__ = (UniqueConstraint("username"),UniqueConstraint("email"),)

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

### Tables - Project

class ProjectBase(SQLModel):
    name: str = Field(default=None)

class ProjectCreate(ProjectBase):
    users_list: list[int] = None
    users_manage: list[bool] = None

class ProjectOutput(ProjectBase):
    id: Optional[int] = Field(default=None, primary_key=True)
    is_active: bool = True

class Project(ProjectOutput, TimestampModel, DeletedModel, table=True):
    __tablename__: str = "project"
    users: list['ProjectUserLink'] = Relationship(back_populates="project")

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

### Tables - Project

class FileCreate(SQLModel):
    name: str
    filename: str
    size: int
    project_id: int = Field(foreign_key="project.id")

class File(FileCreate, TimestampModel, DeletedModel, table=True):
    __tablename__: str = "file"
    id: Optional[int] = Field(default=None, primary_key=True)

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

