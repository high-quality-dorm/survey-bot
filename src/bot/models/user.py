from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from bot.db import Base


class User(Base):
    __tablename__ = "bot_users"
    tg_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, unique=True, nullable=False
    )
    core_id: Mapped[str] = mapped_column(nullable=True)
