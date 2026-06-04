from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from database import get_db
import models
from routers import auth, users, curriculum, content
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Exam Sync API",
    description="Backend API for Exam Sync - Exam Preparation Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(curriculum.router)
app.include_router(content.router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "v1.0.2-debug-1"}

print("\n!!! SERVER RESTARTED - RELOAD WORKING - V1.0.6 !!!\n")

# Admin Secret Route
@app.get("/admin2005")
def admin_secret_route():
    # Redirect to the hidden admin login page
    return RedirectResponse(url="/admin_login.html")

# Mount static files from the parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Mount uploads directory
uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

app.mount("/", StaticFiles(directory=parent_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
