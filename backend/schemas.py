from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class UserRole(str, Enum):
    student = "student"
    author = "author"
    admin = "admin"

# User Schemas
class UserBase(BaseModel):
    username: Optional[str] = None
    email: str
    name: str
    role: UserRole
    branch: Optional[str] = None
    year: Optional[int] = None
    semester: Optional[int] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None

class ProfileUpdate(BaseModel):
    year: Optional[int] = None
    branch: Optional[str] = None
    semester: Optional[int] = None

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserWithSubjects(User):
    assigned_subjects: List[int] = []

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class SignupRequest(BaseModel):
    username: Optional[str] = None
    name: str
    email: str
    password: str
    role: UserRole
    branch: Optional[str] = None
    year: Optional[int] = None
    semester: Optional[int] = None

class OTPRequest(BaseModel):
    email: str

class VerifyOTPRequest(BaseModel):
    email: str
    otp: str

class ForgotPasswordRequest(BaseModel):
    email: str
    name: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

# Subject Schemas
class SubjectBase(BaseModel):
    name: str
    code: str
    theme_config: Optional[dict] = None

class SubjectCreate(SubjectBase):
    semester_id: int

class Subject(SubjectBase):
    id: int
    semester_id: int
    theme_config: Optional[dict] = None
    
    class Config:
        from_attributes = True

# Semester Schemas
class SemesterBase(BaseModel):
    semester_name: str

class Semester(SemesterBase):
    id: int
    year_id: int
    subjects: List[Subject] = []
    
    class Config:
        from_attributes = True

# Year Schemas
class YearBase(BaseModel):
    year_name: str

class Year(YearBase):
    id: int
    semesters: List[Semester] = []
    
    class Config:
        from_attributes = True

# Course Outcome Schemas
class CourseOutcomeBase(BaseModel):
    outcome_text: str
    order: int
    co_no: Optional[str] = None
    unit: Optional[str] = None

class CourseOutcomeCreate(CourseOutcomeBase):
    subject_id: int

class CourseOutcome(CourseOutcomeBase):
    id: int
    subject_id: int
    author_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# PYQ Schemas
class PYQBase(BaseModel):
    link: Optional[str] = None
    year: Optional[int] = Field(None, description="Exam year")
    name: Optional[str] = Field(None, description="Author name or subject identifier")
    image_url: Optional[str] = None

class PYQCreate(PYQBase):
    subject_id: int

class PYQ(PYQBase):
    id: int
    subject_id: int
    author_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# Important Question Schemas
class ImportantQuestionBase(BaseModel):
    question_text: str
    marks: int
    unit: Optional[str] = None
    topic: Optional[str] = None
    image_url: Optional[str] = None

class ImportantQuestionCreate(ImportantQuestionBase):
    subject_id: int

class ImportantQuestion(ImportantQuestionBase):
    id: int
    subject_id: int
    author_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# Roadmap Step Schemas
class RoadmapStepBase(BaseModel):
    step_number: int
    title: str
    description: str
    image_url: Optional[str] = None

class RoadmapStepCreate(RoadmapStepBase):
    subject_id: int

class RoadmapStep(RoadmapStepBase):
    id: int
    subject_id: int
    author_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# Note Schemas
class NoteBase(BaseModel):
    title: str
    file_path: Optional[str] = None

class NoteCreate(NoteBase):
    subject_id: int

class Note(NoteBase):
    id: int
    subject_id: int
    author_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# Doubt Session Schemas
class DoubtSessionBase(BaseModel):
    title: str
    date: str
    time_from: str
    time_to: str
    zoom_link: str

class DoubtSessionCreate(DoubtSessionBase):
    subject_id: int

class DoubtSession(DoubtSessionBase):
    id: int
    subject_id: int
    author_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# Reference Video Schemas
class ReferenceVideoBase(BaseModel):
    unit: Optional[str] = None
    topic: str
    video_link: str

class ReferenceVideoCreate(ReferenceVideoBase):
    subject_id: int

class ReferenceVideo(ReferenceVideoBase):
    id: int
    subject_id: int
    author_id: Optional[int] = None
    
    class Config:
        from_attributes = True

# Subject Content (combined response)
class SubjectContent(BaseModel):
    subject: Subject
    course_outcomes: List[CourseOutcome] = []
    pyqs: List[PYQ] = []
    important_questions: List[ImportantQuestion] = []
    roadmap_steps: List[RoadmapStep] = []
    notes: List[Note] = []
    doubt_sessions: List[DoubtSession] = []
    reference_videos: List[ReferenceVideo] = []
