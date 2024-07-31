from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Option(Base):
    __tablename__ = "option"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    value: Mapped[str] = mapped_column(String)

    def __repr__(self) -> str:
        return f"Option(id={self.id!r}, value={self.name!r})"

class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"

