from typing import List, Optional

from pydantic import BaseModel

class AkademyGradeAddSchema(BaseModel):
    user_id: int
    course_id: int
    grade: float

class DeanGradeAddSchema(BaseModel):
    user_id: int
    course_id: int
    count_of_retake: int
    grade: float

class UserAddSchema(BaseModel):
    name: str
    login: str
    password: str
    is_login: Optional[bool] = None

class CourseAddSchema(BaseModel):
    course: int
    teacher_name: str
    course_name: str
    weight: float

class AchievementFileSchema(BaseModel):
    file_path: str
    file_type: str

class AchievementAddSchema(BaseModel):
    user_tg_id: int
    status: str
    category_id: int
    grade: float
    description: Optional[str] = None
    file_info: AchievementFileSchema

class WebAchievementAddSchema(BaseModel):
    login: str
    user_tg_id: int
    categories: List[str]
    description: Optional[str]
    file_info: AchievementFileSchema

class UserTgAddSchema(BaseModel):
    user_id: int
    is_banned: bool
    tg_name: str