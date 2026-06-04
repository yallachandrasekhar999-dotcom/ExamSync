from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from json_db import JSONDatabase
from typing import List
import models
import schemas
from database import get_db
from auth import get_current_active_user, require_role
from fastapi import Body

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/")
def list_users(
    role: str = None,
    current_user: models.User = Depends(require_role(["admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """List all users (admin only), optionally filter by role"""
    users = db.read("users")
    if role:
        users = [u for u in users if u["role"] == role]
    return users

@router.get("/{user_id}", response_model=schemas.User)
def get_user(
    user_id: int,
    current_user: models.User = Depends(require_role(["admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Get user by ID (admin only)"""
    user = db.get_by_id("users", user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate,
    current_user: models.User = Depends(require_role(["admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Create a new user (admin only)"""
    from auth import get_password_hash
    
    # Check if username exists
    users = db.read("users")
    if any(u["username"] == user.username for u in users):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    db_user = {
        "username": user.username,
        "name": user.name,
        "role": user.role,
        "password_hash": get_password_hash(user.password),
        "created_at": datetime.utcnow().isoformat()
    }
    return db.add("users", db_user)

@router.put("/me/profile", response_model=schemas.User)
def update_my_profile(
    profile: schemas.ProfileUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: JSONDatabase = Depends(get_db)
):
    """Allow authenticated user to update their own academic profile (year, branch, semester)"""
    updates = {}
    if profile.year is not None:
        updates["year"] = profile.year
    if profile.branch is not None:
        updates["branch"] = profile.branch
    if profile.semester is not None:
        updates["semester"] = profile.semester

    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    return db.update("users", current_user.id, updates)

@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(require_role(["admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Update user (admin only)"""
    from auth import get_password_hash
    
    item = db.get_by_id("users", user_id)
    if not item:
        raise HTTPException(status_code=404, detail="User not found")
    
    updates = {}
    if user_update.name:
        updates["name"] = user_update.name
    if user_update.password:
        updates["password_hash"] = get_password_hash(user_update.password)
    
    return db.update("users", user_id, updates)

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: models.User = Depends(require_role(["admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Delete user (admin only)"""
    if not db.delete("users", user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

@router.put("/{user_id}/subjects")
def assign_subjects_to_author(
    user_id: int,
    subject_ids: List[int] = Body(...),
    current_user: models.User = Depends(require_role(["admin"])),
    db: JSONDatabase = Depends(get_db)
):
    """Assign subjects to an author"""
    user = db.get_by_id("users", user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"Target User (ID: {user_id}) not found")
    
    if user["role"] != "author":
        raise HTTPException(status_code=400, detail="User is not an author")
    
    # Merge existing assignments with new ones, avoiding duplicates
    all_assignments = db.read("author_subjects")
    existing_user_subs = {a["subject_id"] for a in all_assignments if a["author_id"] == user_id}
    
    new_subs_added = 0
    for s_id in subject_ids:
        if s_id not in existing_user_subs:
            all_assignments.append({"author_id": user_id, "subject_id": s_id})
            new_subs_added += 1
    
    if new_subs_added > 0:
        db.write("author_subjects", all_assignments)
        
    return {"message": f"Successfully added {new_subs_added} new subjects. Total subjects: {len(existing_user_subs) + new_subs_added}"}


@router.get("/me/subjects", response_model=List[schemas.Subject])
def get_my_assigned_subjects(
    current_user: models.User = Depends(get_current_active_user),
    db: JSONDatabase = Depends(get_db)
):
    """Get subjects assigned to the logged-in author"""
    if current_user.role != "author":
        return []
    
    assignments = db.read("author_subjects")
    subject_ids = [a["subject_id"] for a in assignments if a["author_id"] == current_user.id]
    
    # Fetch subject details for these IDs using the new resolver
    from .curriculum import resolve_subject_by_id
    
    assigned_subjects = []
    for subject_id in subject_ids:
        subject = resolve_subject_by_id(subject_id)
        if subject:
            assigned_subjects.append(subject)
            
    return assigned_subjects
