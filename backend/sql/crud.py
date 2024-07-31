from sqlalchemy.orm import Session
from sqlalchemy import or_
import bcrypt

from . import models, schemas

# Avoided use of passlib
# https://github.com/pyca/bcrypt/issues/684

# from passlib.context import CryptContext
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password):
#     return pwd_context.hash(password)

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
    return bcrypt.checkpw(password = password_byte_enc , hashed_password = hashed_password)



# def get_user(db: Session, user_id: int):
#     return db.query(models.User).filter(models.User.id == user_id).first()


    # stmt = select(User).where(or_(User.username == username, User.email == username))
    # user = db.scalars(stmt).first()

def get_user_by_username_or_email(db: Session, username: str, email: str = None):
    if email:
        return db.query(models.User).filter(or_(models.User.username == username, models.User.email == email)).first()
    return db.query(models.User).filter(or_(models.User.username == username, models.User.email == username)).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate, is_admin: bool = False):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(**user.dict())
    db_user.password = hashed_password
    db_user.is_admin = is_admin
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()


# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = models.Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item