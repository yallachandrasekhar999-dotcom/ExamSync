from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
import enum

# Enum for user roles
class UserRole(str, enum.Enum):
    student = "student"
    author = "author"
    admin = "admin"

class User(BaseModel):
    id: Optional[int] = None
    username: Optional[str] = None
    email: str
    password_hash: str
    name: str
    role: UserRole
    branch: Optional[str] = None  # CSE, ECE, EEE, IT, MECH, AIML, AIDS
    year: Optional[int] = None  # 1, 2, 3, 4
    semester: Optional[int] = None  # For students (1-8)
    created_at: datetime = datetime.utcnow()
    
    model_config = ConfigDict(from_attributes=True)

class CurriculumYear(BaseModel):
    id: Optional[int] = None
    year_name: str
    
    model_config = ConfigDict(from_attributes=True)

class Semester(BaseModel):
    id: Optional[int] = None
    year_id: int
    semester_name: str
    
    model_config = ConfigDict(from_attributes=True)

class Subject(BaseModel):
    id: Optional[int] = None
    semester_id: int
    name: str
    code: str
    
    model_config = ConfigDict(from_attributes=True)

class CourseOutcome(BaseModel):
    id: Optional[int] = None
    subject_id: int
    author_id: Optional[int] = None
    outcome_text: str
    order: int
    
    model_config = ConfigDict(from_attributes=True)

class PYQ(BaseModel):
    id: Optional[int] = None
    subject_id: int
    author_id: Optional[int] = None
    title: str
    link: str
    year: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)

class ImportantQuestion(BaseModel):
    id: Optional[int] = None
    subject_id: int
    author_id: Optional[int] = None
    question_text: str
    marks: int
    
    model_config = ConfigDict(from_attributes=True)

class RoadmapStep(BaseModel):
    id: Optional[int] = None
    subject_id: int
    author_id: Optional[int] = None
    step_number: int
    title: str
    description: str
    
    model_config = ConfigDict(from_attributes=True)

class AuthorSubject(BaseModel):
    author_id: int
    subject_id: int

class Note(BaseModel):
    id: Optional[int] = None
    subject_id: int
    author_id: Optional[int] = None
    title: str
    file_path: str # PDF or Image
    
    model_config = ConfigDict(from_attributes=True)

class DoubtSession(BaseModel):
    id: Optional[int] = None
    subject_id: int
    author_id: Optional[int] = None
    title: str
    date: str # YYYY-MM-DD
    time_from: str # HH:MM
    time_to: str # HH:MM
    zoom_link: str
    
    model_config = ConfigDict(from_attributes=True)

class ReferenceVideo(BaseModel):
    id: Optional[int] = None
    subject_id: int
    author_id: Optional[int] = None
    unit: Optional[str] = None
    topic: str
    video_link: str
    
    model_config = ConfigDict(from_attributes=True)
