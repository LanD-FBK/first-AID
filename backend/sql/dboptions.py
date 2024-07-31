from sqlalchemy import select

from .database import SessionLocal
from .models import Option

def getOption(key, ret_type=str):
    db = SessionLocal()
    stmt = select(Option).where(Option.id == key)
    f = db.scalars(stmt).first()
    if not f:
        return None
    return ret_type(f.value)

def saveOption(key, value, overwrite=True):
    db = SessionLocal()
    key_query = Option(id=key, value=value)
    if overwrite:
        # If the key exists, the value is replaced
        db.merge(key_query)
    else:
        if not getOption(key):
            db.add(key_query)

    db.commit()
