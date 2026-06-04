"""
Script to run the FastAPI backend server
"""
import uvicorn

if __name__ == "__main__":
    print("Starting Exam Sync API Server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Press CTRL+C to stop the server")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
