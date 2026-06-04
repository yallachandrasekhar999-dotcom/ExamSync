from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from json_db import JSONDatabase
from typing import List, Optional
import json
import os
import uuid
import shutil
import models
import schemas
from database import get_db
from auth import get_current_active_user, require_role

router = APIRouter(prefix="/api/content", tags=["content"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "uploads")

def save_upload_file(upload_file: UploadFile) -> str:
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    file_extension = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return f"/uploads/{unique_filename}"

def resolve_subject(subject_id: int, db: JSONDatabase):
    """Resolve a subject by ID — handles both DB subjects and college subjects from subjects.json"""
    from .curriculum import SUBJECTS_FILE, get_subject_theme, BRANCH_MAPPING
    
    # Check if it's a subjects.json ID (deterministic math)
    branch_idx = subject_id // 10000
    semester = (subject_id % 10000) // 100
    index = subject_id % 100
    
    if branch_idx < 100: # Threshold for deterministic IDs vs auto-increment IDs
        if not os.path.exists(SUBJECTS_FILE):
            return None
            
        with open(SUBJECTS_FILE, "r") as f:
            data = json.load(f)
            
        branch_name = next((k for k, v in BRANCH_MAPPING.items() if v == branch_idx), "First Year")
        
        try:
            if branch_name == "First Year":
                subjects = data.get("first_year", {}).get("subjects", [])
            else:
                subjects = data.get("branches", {}).get(branch_name, {}).get("semesters", {}).get(f"sem{semester}", {}).get("subjects", [])
                
            if 0 <= index < len(subjects):
                sub = subjects[index]
                sub_name = sub.get("name") if isinstance(sub, dict) else sub
                return {
                    "id": subject_id,
                    "name": sub_name,
                    "code": sub.get("code", f"CORE-{branch_name}-{semester}-{index+1}") if isinstance(sub, dict) else f"CORE-{branch_name}-{semester}-{index+1}",
                    "semester_id": semester,
                    "theme_config": get_subject_theme(sub_name),
                    "raw_outcomes": sub.get("course_outcomes", []) if isinstance(sub, dict) else []
                }
        except Exception:
            pass
        return None
    else:
        # Fallback to DB subjects for large IDs or auto-increment
        return db.get_by_id("subjects", subject_id)

@router.get("/subjects/{subject_id}", response_model=schemas.SubjectContent)
def get_subject_content(
    subject_id: int,
    author_id: Optional[int] = None,
    current_user: models.User = Depends(get_current_active_user),
    db: JSONDatabase = Depends(get_db)
):
    """Get all content for a subject (handles both deterministic and legacy IDs)"""
    subject = resolve_subject(subject_id, db)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    # Deterministic IDs for First Year map to Legacy IDs (index + 1000)
    query_ids = [subject_id]
    if subject_id < 10000:
        index = subject_id % 100
        legacy_id = index + 1000
        if legacy_id != subject_id:
            query_ids.append(legacy_id)
    
    # Query content using both possible IDs and filter by author_id if provided
    def filter_content(table):
        items = [i for i in db.read(table) if i["subject_id"] in query_ids]
        if author_id is not None:
            # If author_id is provided, show content by that author OR content with no author (general)
            return [i for i in items if i.get("author_id") == author_id or i.get("author_id") is None]
        return items

    cos = filter_content("course_outcomes")
    pyqs = filter_content("pyqs")
    questions = filter_content("important_questions")
    steps = filter_content("roadmap_steps")
    notes = filter_content("notes")
    doubt_sessions = filter_content("doubt_sessions")
    videos = filter_content("reference_videos")
    
    # Fallback to curriculum outcomes if none in DB
    if not cos and subject.get("raw_outcomes"):
        cos = [{"id": 0, "subject_id": subject_id, "outcome_text": text, "order": i} 
               for i, text in enumerate(subject["raw_outcomes"])]

    return {
        "subject": subject,
        "course_outcomes": cos,
        "pyqs": pyqs,
        "important_questions": questions,
        "roadmap_steps": sorted(steps, key=lambda x: x["step_number"] if isinstance(x.get("step_number"), int) else 0),
        "notes": notes,
        "doubt_sessions": doubt_sessions,
        "reference_videos": videos
    }

# Helper to check permissions
def check_assignment(user, subject_id, db):
    if user.role == "admin":
        return True
    assignments = db.read("author_subjects")
    return any(a["author_id"] == user.id and a["subject_id"] == subject_id for a in assignments)

# Course Outcomes
@router.post("/subjects/{subject_id}/cos", response_model=schemas.CourseOutcome)
def add_course_outcome(
    subject_id: int,
    outcome_text: str = Form(...),
    order: int = Form(...),
    co_no: Optional[str] = Form(None),
    unit: Optional[str] = Form(None),
    current_user: models.User = Depends(require_role(["author", "admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Add a course outcome to a subject"""
    subject = resolve_subject(subject_id, db)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    if not check_assignment(current_user, subject_id, db):
        raise HTTPException(status_code=403, detail="Not assigned to this subject")
    
    item = {
        "subject_id": subject_id,
        "author_id": current_user.id,
        "outcome_text": outcome_text,
        "order": order,
        "co_no": co_no,
        "unit": unit
    }
    return db.add("course_outcomes", item)

@router.delete("/cos/{co_id}")
def delete_course_outcome(
    co_id: int,
    current_user: models.User = Depends(require_role(["author", "admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Delete a course outcome"""
    item = db.get_by_id("course_outcomes", co_id)
    if not item:
        raise HTTPException(status_code=404, detail="Course outcome not found")
    
    if not check_assignment(current_user, item["subject_id"], db):
        raise HTTPException(status_code=403, detail="Not permitted for this subject")

    db.delete("course_outcomes", co_id)
    return {"message": "Course outcome deleted"}

# PYQs
@router.post("/subjects/{subject_id}/pyqs", response_model=schemas.PYQ)
def add_pyq(
    subject_id: int,
    name: Optional[str] = Form(None),
    year: Optional[int] = Form(None),
    link: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: models.User = Depends(require_role(["author", "admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Add a PYQ to a subject"""
    subject = resolve_subject(subject_id, db)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    if not check_assignment(current_user, subject_id, db):
        raise HTTPException(status_code=403, detail="Not assigned to this subject")
    
    image_url = None
    if file:
        image_url = save_upload_file(file)
    
    item = {
        "subject_id": subject_id,
        "author_id": current_user.id,
        "name": name,
        "year": year,
        "link": link,
        "image_url": image_url
    }
    return db.add("pyqs", item)

@router.delete("/pyqs/{pyq_id}")
def delete_pyq(
    pyq_id: int,
    current_user: models.User = Depends(require_role(["author", "admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Delete a PYQ"""
    item = db.get_by_id("pyqs", pyq_id)
    if not item:
        raise HTTPException(status_code=404, detail="PYQ not found")
    
    if not check_assignment(current_user, item["subject_id"], db):
        raise HTTPException(status_code=403, detail="Not permitted for this subject")

    db.delete("pyqs", pyq_id)
    return {"message": "PYQ deleted"}

# Important Questions
@router.post("/subjects/{subject_id}/questions", response_model=schemas.ImportantQuestion)
def add_important_question(
    subject_id: int,
    question_text: str = Form(...),
    marks: int = Form(...),
    unit: Optional[str] = Form(None),
    topic: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: models.User = Depends(require_role(["author", "admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Add an important question to a subject"""
    subject = resolve_subject(subject_id, db)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    if not check_assignment(current_user, subject_id, db):
        raise HTTPException(status_code=403, detail="Not assigned to this subject")
    
    image_url = None
    if file:
        image_url = save_upload_file(file)
    
    item = {
        "subject_id": subject_id,
        "author_id": current_user.id,
        "question_text": question_text,
        "marks": marks,
        "unit": unit,
        "topic": topic,
        "image_url": image_url
    }
    return db.add("important_questions", item)

@router.delete("/questions/{question_id}")
def delete_important_question(
    question_id: int,
    current_user: models.User = Depends(require_role(["author", "admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Delete an important question"""
    item = db.get_by_id("important_questions", question_id)
    if not item:
        raise HTTPException(status_code=404, detail="Question not found")
    
    if not check_assignment(current_user, item["subject_id"], db):
        raise HTTPException(status_code=403, detail="Not permitted for this subject")

    db.delete("important_questions", question_id)
    return {"message": "Question deleted"}

# Roadmap Steps
@router.post("/subjects/{subject_id}/roadmap", response_model=schemas.RoadmapStep)
def add_roadmap_step(
    subject_id: int,
    step_number: int = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    file: Optional[UploadFile] = File(None),
    current_user: models.User = Depends(require_role(["author", "admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Add a roadmap step to a subject"""
    subject = resolve_subject(subject_id, db)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    if not check_assignment(current_user, subject_id, db):
        raise HTTPException(status_code=403, detail="Not assigned to this subject")
    
    image_url = None
    if file:
        image_url = save_upload_file(file)
    
    item = {
        "subject_id": subject_id,
        "author_id": current_user.id,
        "step_number": step_number,
        "title": title,
        "description": description,
        "image_url": image_url
    }
    return db.add("roadmap_steps", item)

@router.delete("/roadmap/{step_id}")
def delete_roadmap_step(
    step_id: int,
    current_user: models.User = Depends(require_role(["author", "admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Delete a roadmap step"""
    item = db.get_by_id("roadmap_steps", step_id)
    if not item:
        raise HTTPException(status_code=404, detail="Roadmap step not found")
    
    if not check_assignment(current_user, item["subject_id"], db):
        raise HTTPException(status_code=403, detail="Not permitted for this subject")

    db.delete("roadmap_steps", step_id)
    return {"message": "Roadmap step deleted"}

# Notes
@router.post("/subjects/{subject_id}/notes", response_model=schemas.Note)
def add_note(
    subject_id: int,
    title: str = Form(...),
    file: UploadFile = File(...),
    current_user: models.User = Depends(require_role(["author", "admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Add a note to a subject"""
    if not check_assignment(current_user, subject_id, db):
        raise HTTPException(status_code=403, detail="Not assigned to this subject")
    
    file_path = save_upload_file(file)
    item = {"subject_id": subject_id, "author_id": current_user.id, "title": title, "file_path": file_path}
    return db.add("notes", item)

@router.delete("/notes/{note_id}")
def delete_note(
    note_id: int,
    current_user: models.User = Depends(require_role(["author", "admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Delete a note"""
    item = db.get_by_id("notes", note_id)
    if not item or not check_assignment(current_user, item["subject_id"], db):
        raise HTTPException(status_code=403, detail="Unauthorized")
    db.delete("notes", note_id)
    return {"message": "Note deleted"}

# Doubt Sessions
@router.post("/subjects/{subject_id}/doubt_sessions", response_model=schemas.DoubtSession)
def add_doubt_session(
    subject_id: int,
    title: str = Form(...),
    date: str = Form(...),
    time_from: str = Form(...),
    time_to: str = Form(...),
    zoom_link: str = Form(...),
    current_user: models.User = Depends(require_role(["author", "admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Add a doubt session to a subject"""
    if not check_assignment(current_user, subject_id, db):
        raise HTTPException(status_code=403, detail="Not assigned to this subject")
    
    item = {
        "subject_id": subject_id, 
        "author_id": current_user.id,
        "title": title, 
        "date": date, 
        "time_from": time_from, 
        "time_to": time_to, 
        "zoom_link": zoom_link
    }
    return db.add("doubt_sessions", item)

@router.delete("/doubt_sessions/{session_id}")
def delete_doubt_session(
    session_id: int,
    current_user: models.User = Depends(require_role(["author", "admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Delete a doubt session"""
    item = db.get_by_id("doubt_sessions", session_id)
    if not item or not check_assignment(current_user, item["subject_id"], db):
        raise HTTPException(status_code=403, detail="Unauthorized")
    db.delete("doubt_sessions", session_id)
    return {"message": "Doubt session deleted"}

# Reference Videos
@router.post("/subjects/{subject_id}/videos", response_model=schemas.ReferenceVideo)
def add_reference_video(
    subject_id: int,
    topic: str = Form(...),
    video_link: str = Form(...),
    unit: Optional[str] = Form(None),
    current_user: models.User = Depends(require_role(["author", "admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Add a reference video to a subject"""
    if not check_assignment(current_user, subject_id, db):
        raise HTTPException(status_code=403, detail="Not assigned to this subject")
    
    item = {"subject_id": subject_id, "author_id": current_user.id, "topic": topic, "video_link": video_link, "unit": unit}
    return db.add("reference_videos", item)

@router.delete("/videos/{video_id}")
def delete_reference_video(
    video_id: int,
    current_user: models.User = Depends(require_role(["author", "admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Delete a reference video"""
    item = db.get_by_id("reference_videos", video_id)
    if not item or not check_assignment(current_user, item["subject_id"], db):
        raise HTTPException(status_code=403, detail="Unauthorized")
    db.delete("reference_videos", video_id)
    return {"message": "Video deleted"}

# Assignment & Authors
@router.get("/subjects/{subject_id}/authors", response_model=List[schemas.User])
def get_subject_authors(
    subject_id: int,
    db: JSONDatabase = Depends(get_db)
):
    """Get all authors assigned to a subject"""
    assignments = db.read("author_subjects")
    author_ids = [a["author_id"] for a in assignments if a["subject_id"] == subject_id]
    
    users = db.read("users")
    authors = [u for u in users if u["id"] in author_ids and u["role"] == "author"]
    
    return authors
