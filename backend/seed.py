"""
Seed script to populate the JSON database with initial data
"""
from json_db import db
from auth import get_password_hash
from datetime import datetime

def seed_database():
    print("Seeding database...")
    
    # Check if data already exists
    if db.read("users"):
        print("Database already seeded!")
        return
    
    # Create users
    users = [
        {
            "id": 1,
            "username": "student",
            "password_hash": get_password_hash("123"),
            "name": "Alex Student",
            "role": "student",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": 2,
            "username": "admin",
            "password_hash": get_password_hash("123"),
            "name": "Super Admin",
            "role": "admin",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": 3,
            "username": "author",
            "password_hash": get_password_hash("123"),
            "name": "Dr. Smith",
            "role": "author",
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    db.write("users", users)
    
    # Curriculum Years
    years = [{"id": 1, "year_name": "First Year"}, {"id": 2, "year_name": "Second Year"}]
    db.write("curriculum_years", years)
    
    # Semesters
    semesters = [
        {"id": 1, "year_id": 1, "semester_name": "Semester 1"},
        {"id": 2, "year_id": 1, "semester_name": "Semester 2"},
        {"id": 3, "year_id": 2, "semester_name": "Semester 3"}
    ]
    db.write("semesters", semesters)
    
    # Subjects
    subjects = [
        {"id": 1, "semester_id": 1, "name": "Engineering Mathematics I", "code": "MAT101"},
        {"id": 2, "semester_id": 1, "name": "Engineering Physics", "code": "PHY101"},
        {"id": 3, "semester_id": 2, "name": "Engineering Mathematics II", "code": "MAT102"},
        {"id": 4, "semester_id": 2, "name": "Basic Electronics", "code": "ECE101"},
        {"id": 5, "semester_id": 3, "name": "Data Structures", "code": "CS201"},
        {"id": 6, "semester_id": 3, "name": "Digital Logic", "code": "CS202"}
    ]
    db.write("subjects", subjects)
    
    # Author Subjects
    author_subs = [
        {"author_id": 3, "subject_id": 1},
        {"author_id": 3, "subject_id": 2}
    ]
    db.write("author_subjects", author_subs)
    
    # Course Outcomes for Math1
    cos = [
        {"id": 1, "subject_id": 1, "outcome_text": "CO1: Understand calculus basics.", "order": 1},
        {"id": 2, "subject_id": 1, "outcome_text": "CO2: Apply differential equations.", "order": 2}
    ]
    db.write("course_outcomes", cos)
    
    # PYQs for Math1
    pyqs = [
        {"id": 1, "subject_id": 1, "title": "2023 End Sem", "link": "#", "year": 2023},
        {"id": 2, "subject_id": 1, "title": "2022 End Sem", "link": "#", "year": 2022}
    ]
    db.write("pyqs", pyqs)
    
    # Questions for Math1
    questions = [
        {"id": 1, "subject_id": 1, "question_text": "Explain Leibnitz theorem.", "marks": 5},
        {"id": 2, "subject_id": 1, "question_text": "Solve the differential equation...", "marks": 10}
    ]
    db.write("important_questions", questions)
    
    # Roadmap for Math1
    roadmap = [
        {"id": 1, "subject_id": 1, "step_number": 1, "title": "Limits & Continuity", "description": "Understand the behavior of functions."},
        {"id": 2, "subject_id": 1, "step_number": 2, "title": "Derivatives", "description": "Learn rules of differentiation."},
        {"id": 3, "subject_id": 1, "step_number": 3, "title": "Integrals", "description": "Master definite and indefinite integrals."},
        {"id": 4, "subject_id": 1, "step_number": 4, "title": "Differential Equations", "description": "Solve first and second order DEs."}
    ]
    db.write("roadmap_steps", roadmap)
    
    # Add content for Data Structures
    cos_ds = [
        {"id": 3, "subject_id": 5, "outcome_text": "CO1: Analyze algorithms.", "order": 1},
        {"id": 4, "subject_id": 5, "outcome_text": "CO2: Implement linked lists and trees.", "order": 2}
    ]
    # We append to the file if we want to build it up, but since this is a seed, we can just collect all and write at once in a real script.
    # Here I'll just combine them.
    db.write("course_outcomes", cos + cos_ds)
    
    pyqs_ds = [
        {"id": 3, "subject_id": 5, "title": "2024 Mid Sem", "link": "#", "year": 2024}
    ]
    db.write("pyqs", pyqs + pyqs_ds)
    
    questions_ds = [
        {"id": 3, "subject_id": 5, "question_text": "Difference between BFS and DFS?", "marks": 5},
        {"id": 4, "subject_id": 5, "question_text": "Explain QuickSort algorithm.", "marks": 10}
    ]
    db.write("important_questions", questions + questions_ds)
    
    roadmap_ds = [
        {"id": 5, "subject_id": 5, "step_number": 1, "title": "Arrays & Strings", "description": "Basic manipulation and memory layout."},
        {"id": 6, "subject_id": 5, "step_number": 2, "title": "Linked Lists", "description": "Singly, Doubly, and Circular lists."},
        {"id": 7, "subject_id": 5, "step_number": 3, "title": "Stacks & Queues", "description": "LIFO and FIFO principles."},
        {"id": 8, "subject_id": 5, "step_number": 4, "title": "Trees & Graphs", "description": "Hierarchical data structures and traversals."},
        {"id": 9, "subject_id": 5, "step_number": 5, "title": "Sorting & Searching", "description": "Efficient algorithms for data retrieval."}
    ]
    db.write("roadmap_steps", roadmap + roadmap_ds)
    
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
