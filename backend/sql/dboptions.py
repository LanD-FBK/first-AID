from sqlmodel import select, Session

from .database import engine
from .models import Option


def getOption(key, ret_type=str):
    with Session(engine) as db:
        stmt = select(Option).where(Option.id == key)
        f = db.scalars(stmt).first()
        if not f:
            return None
        return ret_type(f.value)


def saveOption(key, value, overwrite=False):
    with Session(engine) as db:
        key_query = Option(id=key, value=value)
        if overwrite:
            # If the key exists, the value is replaced
            db.merge(key_query)
        else:
            if getOption(key) is None:
                db.add(key_query)

        db.commit()
