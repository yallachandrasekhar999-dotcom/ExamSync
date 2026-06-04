# Exam Sync Backend

FastAPI backend for the Exam Sync application.

## Setup

1. Install Python 3.8+ if not already installed

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Seed the database with initial data:
```bash
python seed.py
```

6. Run the server:
```bash
uvicorn main:app --reload
```

The API will be available at: http://localhost:8000

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Default Users

After seeding, you can login with:
- **Student**: username: `student`, password: `123`
- **Author**: username: `author`, password: `123`
- **Admin**: username: `admin`, password: `123`

## Project Structure

```
backend/
├── main.py              # FastAPI app entry point
├── database.py          # Database configuration
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── auth.py              # Authentication utilities
├── seed.py              # Database seeding script
├── requirements.txt     # Python dependencies
└── routers/
    ├── auth.py          # Authentication endpoints
    ├── users.py         # User management
    ├── curriculum.py    # Curriculum management
    └── content.py       # Content management
```

## Security Note

**IMPORTANT**: Change the `SECRET_KEY` in `auth.py` before deploying to production!
