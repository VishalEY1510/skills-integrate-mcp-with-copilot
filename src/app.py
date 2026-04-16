"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
import os
from pathlib import Path
import uuid

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Pydantic models for authentication
class UserRegistration(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

# In-memory user database
users = {
    "teacher1": {
        "id": "user_001",
        "username": "teacher1",
        "email": "teacher1@mergington.edu",
        "password_hash": generate_password_hash("password123"),
        "role": "admin"
    }
}

# Session tokens mapping (token -> user_id)
sessions = {}

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/auth/register")
def register(user_data: UserRegistration):
    """Register a new user account"""
    # Validate username doesn't already exist
    if user_data.username in users:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )
    
    # Validate password requirements
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters"
        )
    
    # Create new user
    user_id = f"user_{len(users) + 1:03d}"
    users[user_data.username] = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "password_hash": generate_password_hash(user_data.password),
        "role": "student"
    }
    
    return {
        "message": "User registered successfully",
        "user_id": user_id,
        "username": user_data.username,
        "role": "student"
    }


@app.post("/auth/login")
def login(credentials: UserLogin):
    """Login with username and password"""
    # Check if user exists
    if credentials.username not in users:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    user = users[credentials.username]
    
    # Verify password
    if not check_password_hash(user["password_hash"], credentials.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    # Generate session token
    token = str(uuid.uuid4())
    sessions[token] = user["id"]
    
    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
        }
    }


@app.get("/auth/me")
def get_current_user(token: str):
    """Get current user information"""
    # Check if token exists
    if token not in sessions:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    user_id = sessions[token]
    
    # Find user by ID
    for user in users.values():
        if user["id"] == user_id:
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"]
            }
    
    raise HTTPException(
        status_code=404,
        detail="User not found"
    )


@app.post("/auth/logout")
def logout(token: str):
    """Logout and invalidate session token"""
    if token in sessions:
        del sessions[token]
        return {"message": "Logout successful"}
    
    raise HTTPException(
        status_code=400,
        detail="Invalid token"
    )

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
