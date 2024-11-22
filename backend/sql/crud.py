from datetime import datetime
from typing import Type

import bcrypt
from sqlmodel import Session, or_, select, SQLModel

from sql.models import DeletedModel
from sql.models import Project, ProjectCreate, ProjectUserLink
from sql.models import User, UserCreate


### GENERIC FUNCTIONS

def get_existing_elements(db: Session, obj_type: Type[SQLModel]):
    statement = db.query(obj_type)
    if issubclass(obj_type, DeletedModel):
        statement = statement.filter(obj_type.is_deleted == False)
    return statement


def get_object_by_id(db: Session, obj_id: int, obj_type: Type[SQLModel]):
    statement = get_existing_elements(db, obj_type)
    statement = statement.filter(obj_type.id == obj_id)
    return statement.first()


### LOGIN-RELATED FUNCTIONS

def get_password_hash(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password


# Check if the provided password matches the stored password (hashed)
def verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    if type(hashed_password) == str:
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password)


### USERS

def get_existing_users(db):
    return db.query(User).filter(User.is_deleted == False)


def get_user_by_username_or_email(db: Session, username: str, email: str = None):
    if email:
        return get_existing_users(db).filter(or_(User.username == username, User.email == email)).first()
    return get_existing_users(db).filter(or_(User.username == username, User.email == username)).first()


def get_user_by_email(db: Session, email: str):
    return get_existing_users(db).filter(User.email == email).first()


def get_user_by_id(db: Session, id: int):
    return get_existing_users(db).filter(User.id == id).first()


def get_user_by_username(db: Session, username: str):
    return get_existing_users(db).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return get_existing_users(db).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate, is_admin: bool = False):
    db_obj = User.model_validate(
        user, update={"password": get_password_hash(user.password)}
    )
    db_obj.is_admin = is_admin
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def change_active_state(db: Session, db_user: User):
    db_user.is_active = not db_user.is_active
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, db_user: User):
    db_user.is_deleted = True

    # Username and e-mail are modified to avoid conflicts in DB
    # upon re-creation of the same users, since the records are
    # not deleted, but just hidden using soft deletion paradigm
    ts_del = str(datetime.now().timestamp())
    db_user.username = db_user.username + "***deleted***" + ts_del
    db_user.email = db_user.email + "***deleted***" + ts_del

    statement = select(ProjectUserLink).where(ProjectUserLink.user_id == db_user.id)
    results = db.exec(statement).all()
    for record in results:
        db.delete(record)
    db.add(db_user)
    db.commit()


def edit_user(db: Session, db_user: User, user: UserCreate):
    if user.password:
        user.password = get_password_hash(user.password)
    else:
        user.password = db_user.password
    db_user.sqlmodel_update(user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def change_password(db: Session, db_user: User, new_password: str):
    setattr(db_user, "password", get_password_hash(new_password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


### PROJECTS

def get_projects(db: Session, user: User, skip: int = 0, limit: int = 100):
    statement = get_existing_elements(db, Project)
    if not user.is_admin:
        statement = (
            statement
            .join(ProjectUserLink, isouter=True)  # Probably isouter is not needed here
            .where(ProjectUserLink.user_id == user.id)
        )
    return (
        statement
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_project(db: Session, project: ProjectCreate, users: list):
    pr_db_obj = Project.model_validate(project)
    db.add(pr_db_obj)
    if users is not None:
        for user in users:
            db_obj = ProjectUserLink(project=pr_db_obj, user=user[0], is_project_admin=user[1])
            db.add(db_obj)
    db.commit()
    db.refresh(pr_db_obj)
    return pr_db_obj


def edit_project(db: Session, db_project: Project, project: ProjectCreate, users: list):
    # First I need to "remove" the fields not present in the DB (such as users_manage)
    # otherwise the sqlmodel_update returns an error (this should be a suggestion for a fix)

    # I need to make a copy of the ID for some reason (otherwise it's None)
    project_data = project.model_dump(exclude_unset=True)
    db_project.sqlmodel_update(project_data)

    # pr_db_obj = Project.model_validate(project)
    # id_old = db_project.id
    #
    # db_project.sqlmodel_update(pr_db_obj)
    # db_project.id = id_old
    db.add(db_project)

    if users is not None:
        # Delete existing links between project and users
        statement = select(ProjectUserLink).where(ProjectUserLink.project_id == db_project.id)
        results = db.exec(statement).all()
        for record in results:
            db.delete(record)

        for user in users:
            db_obj = ProjectUserLink(project=db_project, user=user[0], is_project_admin=user[1])
            db.add(db_obj)

    db.commit()
    db.refresh(db_project)
    return db_project


def assign_user_to_project(db: Session, project_id: int, user_id: int, user_manage: bool):
    db_project = get_object_by_id(db, project_id, Project)
    db_user = get_object_by_id(db, user_id, User)
    db_obj = db.query(ProjectUserLink).where(ProjectUserLink.project_id == db_project.id).where(
        ProjectUserLink.user_id == db_user.id).first()
    if not db_obj:
        db_obj = ProjectUserLink(project=db_project, user=db_user, is_project_admin=user_manage)
    else:
        db_obj.is_project_admin = user_manage
    db.add(db_obj)
    db.commit()
    db.refresh(db_project)
    return db_project


def revoke_user_from_project(db: Session, project_id: int, user_id: int):
    statement = select(ProjectUserLink) \
        .where(ProjectUserLink.project_id == project_id) \
        .where(ProjectUserLink.user_id == user_id)
    results = db.exec(statement).all()
    for record in results:
        db.delete(record)
    db.commit()
    db_project = get_object_by_id(db, project_id, Project)
    return db_project


def delete_project(db: Session, db_project: Project):
    db_project.is_deleted = True
    statement = select(ProjectUserLink).where(ProjectUserLink.project_id == db_project.id)
    results = db.exec(statement).all()
    for record in results:
        db.delete(record)
    db.add(db_project)
    db.commit()
