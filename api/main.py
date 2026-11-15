from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import student, faculty, admin, analytics

app = FastAPI(
    title="Acadendora Academic Attendance & Audit Management System",
    description="SQL-first attendance management and analytics REST API",
    version="1.0.0"
)

# Enable CORS so our frontend HTML pages can call the API smoothly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(student.router,   prefix="/api/student",    tags=["Student Portal"])
app.include_router(faculty.router,   prefix="/api/faculty",    tags=["Faculty Portal"])
app.include_router(admin.router,     prefix="/api/admin",      tags=["Admin Control Panel"])
app.include_router(analytics.router, prefix="/api/analytics",  tags=["Analytics & Query Trace"])

@app.get("/")
def root():
    return {
        "system": "Acadendora Attendance & Audit Management API",
        "status": "Online",
        "docs_url": "http://localhost:8000/docs"
    }