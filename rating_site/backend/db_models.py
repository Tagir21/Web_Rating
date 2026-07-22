from sqlalchemy.dialects.mssql import JSON
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,)
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.sql.expression import text
from typing import Optional, List

class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    login: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))
    study_group_id: Mapped[int] = mapped_column(ForeignKey('study_groups.id'))
    is_login: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    last_event: Mapped[int] = mapped_column(
        Integer,
        server_default= text('(UNIX_TIMESTAMP())'),
        onupdate = text('UNIX_TIMESTAMP()')
    )

    study_group = relationship('StudyGroupModel', back_populates='user')
    akademy_grade = relationship('AkademyGradeModel', back_populates='user')
    dean_grade = relationship('DeanGradeModel', back_populates='user')
    user_tg = relationship('UserTgModel', back_populates='user')

class StudyGroupModel(Base):
    __tablename__ = 'study_groups'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))

    user = relationship('UserModel', back_populates='study_group')

class AkademyGradeModel(Base):
    __tablename__ = 'academy_grades'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id'))
    grade: Mapped[float] = mapped_column(default=0.0)
    last_update: Mapped[int] = mapped_column(
        Integer,
        server_default=text('(UNIX_TIMESTAMP())'),
        onupdate=text('(UNIX_TIMESTAMP())')
    )

    user = relationship('UserModel', back_populates='akademy_grade')
    course = relationship('CourseModel', back_populates='akademy_grade')

class DeanGradeModel(Base):
    __tablename__ = 'dean_grades'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    course_id: Mapped[int] = mapped_column(ForeignKey('courses.id'))
    count_of_retake: Mapped[int] = mapped_column(default=0)
    grade: Mapped[float] = mapped_column(default=0.0)
    last_update: Mapped[int] = mapped_column(
        Integer,
        server_default=text('(UNIX_TIMESTAMP())'),
        onupdate=text('(UNIX_TIMESTAMP())')
    )

    user = relationship('UserModel', back_populates='dean_grade')
    course = relationship('CourseModel', back_populates='dean_grade')

class CourseModel(Base):
    __tablename__ = 'courses'

    id: Mapped[int] = mapped_column(primary_key=True)
    course: Mapped[int]
    teacher_name: Mapped[str] = mapped_column(String(255))
    course_name: Mapped[str] = mapped_column(String(255))
    weight: Mapped[float]
    last_update: Mapped[int] = mapped_column(
        Integer,
        server_default=text('(UNIX_TIMESTAMP())'),
        onupdate=text('(UNIX_TIMESTAMP())')
    )

    akademy_grade = relationship('AkademyGradeModel', back_populates='course')
    dean_grade = relationship('DeanGradeModel', back_populates='course')

class AchievementModel(Base):
    __tablename__ = 'achievements'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_tg_id: Mapped[int] = mapped_column(ForeignKey('telegram_data.id'))
    status: Mapped[str] = mapped_column(String(30), default='viewing')
    category_id: Mapped[List[int]] = mapped_column(JSON, nullable=False)
    grade: Mapped[float] = mapped_column(default=0.0)
    description: Mapped[Optional[str]] = mapped_column(String(500), default=None, server_default=text('NULL'))
    file_path: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(30))
    created_at: Mapped[int] = mapped_column(
        Integer,
        server_default=text('(UNIX_TIMESTAMP())')
    )

    user_tg = relationship('UserTgModel', back_populates='achievement')

class UserTgModel(Base):
    __tablename__ = 'telegram_data'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    is_banned: Mapped[bool] = mapped_column(default=False, server_default=text('false'))
    tg_name: Mapped[str] = mapped_column(String(255))

    user = relationship('UserModel', back_populates='user_tg')
    achievement = relationship('AchievementModel', back_populates='user_tg')

class CategoryDataModel(Base):
    __tablename__ = 'category_data'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    alias: Mapped[str] = mapped_column(String(255))
    weight: Mapped[int] = mapped_column(default=1)

