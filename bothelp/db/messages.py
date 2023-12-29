import datetime

from sqlalchemy import func, BigInteger, ARRAY, Column, Integer, TEXT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class Message(BaseModel):
    __tablename__ = "messages"

    _id: Mapped[int] = mapped_column(BigInteger, autoincrement=True, unique=True, nullable=False, primary_key=True)
    text: Mapped[str] = mapped_column(TEXT, unique=False, nullable=True)
    image_id: Mapped[str] = mapped_column(VARCHAR, unique=True, nullable=True)
    send_at: Mapped[datetime.datetime] = mapped_column(unique=False, nullable=True, server_default=func.now())

    from_user_id: Mapped[int] = mapped_column(BigInteger, unique=False, nullable=False)
    message_and_recipient_ids = Column(ARRAY(Integer), unique=False, nullable=True)
