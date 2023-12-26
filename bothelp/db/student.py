import datetime

from sqlalchemy import func, BigInteger, ARRAY, VARCHAR, Column, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class Student(BaseModel):
    __tablename__ = "students"

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, primary_key=True)
    login: Mapped[str] = mapped_column(unique=False, nullable=True)
    password: Mapped[str] = mapped_column(unique=False, nullable=True)
    csrf_token: Mapped[str] = mapped_column(unique=False, nullable=True)
    session_id: Mapped[str] = mapped_column(unique=False, nullable=True)
    student_id: Mapped[int] = mapped_column(unique=True, nullable=True)

    site_prefix: Mapped[str] = mapped_column(unique=False, nullable=True)
    current_quarter: Mapped[int] = mapped_column(unique=False, nullable=True)
    full_quarter: Mapped[int] = mapped_column(unique=False, nullable=True)

    reg_date: Mapped[datetime.datetime] = mapped_column(unique=False, nullable=True, server_default=func.now())
    upd_date: Mapped[datetime.datetime] = mapped_column(unique=False, nullable=True, server_onupdate=func.now())

    # Student settings
    full_view_model: Mapped[bool] = mapped_column(unique=False, default=False)
    alarm_state: Mapped[bool] = mapped_column(unique=False, default=False)
    alarm_lessons = Column(ARRAY(VARCHAR), unique=False, default=['*'])

    admin_level: Mapped[int] = Column(Integer, unique=False, nullable=False, default=0)

    lessons_cache = Column(ARRAY(VARCHAR), unique=False, nullable=True)

    is_block: Mapped[bool] = Column(Boolean, unique=False, nullable=False, serdefault=False)

    def __str__(self) -> str:
        return f'<Student:{self.user_id}>'
