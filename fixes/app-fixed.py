"""
The key difference: User input is NEVER concatenated into SQL strings.
Instead, queries are parameterized - input is treated as DATA, not CODE.
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import uvicorn

from backend.database import engine, SessionLocal, Base, get_db
from backend.models import User

# Creates tables when app starts
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Secure API - SQL Injection Fixed")

# Enable CORS for frontend communication

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# STARTUP EVENT - Creates the test data

@app.on_event("startup")
def startup_event():
    """Creates test users in the database"""
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.username == "admin").first()
        if not existing_user:
            test_users = [
                User(username="admin", password="admin_password_123", email="admin@example.com"),
                User(username="john", password="john_password_456", email="john@example.com"),
                User(username="jane", password="jane_password_789", email="jane@example.com"),
                User(username="peter", password="peter_password_101", email="peter@example.com"),
                User(username="alice", password="alice_password_202", email="alice@example.com"),
                User(username="jack", password="jack_password_303", email="jack@example.com"),
                User(username="emily", password="emily_password_404", email="emily@example.com"),
            ]
            db.add_all(test_users)
            db.commit()
            print("✓ Test users created")
        else:
            print("✓ Test users already exist")
    finally:
        db.close()


# SECURE ENDPOINT #1: Login with Parameterized Query

@app.post("/login-secure")
def login_secure(username: str, password: str, db: Session = Depends(get_db)):
    """
    SECURE endpoint - SQL Injection PREVENTED
    
    Security measures:
    1. Uses parameterized query with named parameters
    2. Database engine handles escaping
    3. User input treated as DATA, not CODE
    4. SQL injection impossible because:
       - Even if username = "admin' --"
       - The database treats the ENTIRE string as a username value
       - The -- is not interpreted as a comment
    
    How it works:
    - Text(sql) with bindings tells SQLAlchemy to use parameterized query
    - The ? placeholders are filled by SQLAlchemy, not Python string formatting
    - Database engine escapes special characters automatically
    """
    
    # SECURE METHOD 1: Using parameterized query with text()
    # The :username and :password are placeholders
    query = text("SELECT * FROM users WHERE username = :username AND password = :password")
    
    print(f"[DEBUG] Executing parameterized query")
    print(f"[DEBUG] Username binding: {username}")
    print(f"[DEBUG] Password binding: {password}")
    
    try:
        # Pass parameters separately - they are bound to placeholders
        result = db.execute(query, {"username": username, "password": password})
        user = result.fetchone()
        
        if user:
            return {
                "success": True,
                "message": "Login successful!",
                "user": {
                    "id": user[0],
                    "username": user[1],
                    "email": user[3]
                }
            }
        else:
            return {
                "success": False,
                "message": "Invalid username or password"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


# SECURE ENDPOINT #2: Login Using SQLAlchemy ORM (BEST PRACTICE)

@app.post("/login-orm")
def login_orm(username: str, password: str, db: Session = Depends(get_db)):
    """
    MOST SECURE endpoint - Uses SQLAlchemy ORM
    
    Why ORM is best:
    1. Never write raw SQL
    2. Completely prevents SQL injection
    3. Cleaner, more Pythonic code
    4. Better type safety
    5. Easier to maintain
    
    The query is built by SQLAlchemy, which handles parameterization automatically.
    You filter by attributes, not by string concatenation.
    """
    
    try:
        # SQLAlchemy ORM query - NO RAW SQL, NO STRING CONCATENATION
        # This is the safest way to query
        user = db.query(User).filter(
            User.username == username,
            User.password == password
        ).first()
        
        if user:
            return {
                "success": True,
                "message": "Login successful!",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            }
        else:
            return {
                "success": False,
                "message": "Invalid username or password"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

# SECURE ENDPOINT #3: Get User by ID (Parameterized)

@app.get("/get-user-secure")
def get_user_secure(user_id: int, db: Session = Depends(get_db)):
    """
    SECURE endpoint - Get user by ID with parameterized query
    
    Security improvements:
    1. Type hint: user_id: int means FastAPI validates it's an integer
    2. Even if someone tries "1 OR 1=1", FastAPI converts to int first
    3. This fails validation because "1 OR 1=1" is not an integer
    4. Parameterized query adds another layer of protection
    
    Defense in depth: Multiple layers of protection
    """
    
    # Type validation happens automatically due to FastAPI type hint
    # FastAPI will reject "1 OR 1=1" because it's not a valid integer
    
    try:
        # Parameterized query with integer placeholder
        query = text("SELECT * FROM users WHERE id = :user_id")
        result = db.execute(query, {"user_id": user_id})
        user = result.fetchone()
        
        if user:
            return {
                "success": True,
                "users": [
                    {
                        "id": user[0],
                        "username": user[1],
                        "email": user[3]
                    }
                ]
            }
        else:
            return {
                "success": False,
                "message": "No user found"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

# SECURE ENDPOINT #4: Get User by ID (ORM - BEST PRACTICE)

@app.get("/get-user-orm")
def get_user_orm(user_id: int, db: Session = Depends(get_db)):
    """
    MOST SECURE endpoint - Get user using ORM
    
    Why this is safest:
    1. Type validation by FastAPI
    2. SQLAlchemy ORM with parameterized queries
    3. No raw SQL at all
    4. Clean, readable code
    """
    
    try:
        # SQLAlchemy ORM - Safest approach
        user = db.query(User).filter(User.id == user_id).first()
        
        if user:
            return {
                "success": True,
                "users": [
                    {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email
                    }
                ]
            }
        else:
            return {
                "success": False,
                "message": "No user found"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }

# REFERENCE: View all users

@app.get("/all-users")
def get_all_users(db: Session = Depends(get_db)):
    """Returns all users in the database"""
    users = db.query(User).all()
    return {
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "password": user.password,
                "email": user.email
            }
            for user in users
        ]
    }


# HEALTH CHECK

@app.get("/")
def read_root():
    """Simple health check endpoint"""
    return {
        "message": "Secure API is running",
        "status": "✅ PROTECTED AGAINST SQL INJECTION ✅"
    }

# Run the app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)