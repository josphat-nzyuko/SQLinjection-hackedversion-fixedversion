

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import uvicorn

from database import engine, SessionLocal, Base, get_db
from models import User

# Creates tables when app starts
Base.metadata.create_all(bind=engine)


app = FastAPI(title="Vulnerable API - SQL Injection Demo")

# Enables CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")

# STARTUP EVENT - Create test data


@app.on_event("startup")
def startup_event():
    
    """Creates test users in the database"""   

    db = SessionLocal()
    try:
        test_users = [
            {"username": "admin", "password": "admin_password_123", "email": "admin@example.com"},
            {"username": "john", "password": "john_password_456", "email": "john@example.com"},
            {"username": "jane", "password": "jane_password_789", "email": "jane@example.com"},
            {"username": "Peter", "password": "peter_password_101", "email": "peter@example.com"},
            {"username": "alice", "password": "alice_password_202", "email": "alice@example.com"},
            {"username": "jack", "password": "jack_password_303", "email": "jack@example.com"},
            {"username": "emily", "password": "emily_password_404", "email": "emily@example.com"},

        ]

        created_count = 0
        for user_data in test_users:
            existing_user = db.query(User).filter(
                User.username == user_data["username"]
            ).first()

            if not existing_user:
                db.add(User(**user_data))
                created_count += 1

        db.commit()

        if created_count:
            print(f"✓ Created {created_count} missing test user(s)")
        else:
            print("✓ All test users already exist")
    finally:
        db.close()

# VULNERABLE ENDPOINT #1: Login with SQL Injection


@app.post("/login-vulnerable")
def login_vulnerable(username: str, password: str, db: Session = Depends(get_db)):
    """
    VULNERABLE endpoint - SQL Injection vulnerability
    
    This endpoint is INTENTIONALLY vulnerable to demonstrate SQL injection
    
    The vulnerability:
    - Takes user input (username, password)
    - Directly concatenates into SQL query string
    - Database executes the concatenated string
    - Attacker can inject SQL commands
    
    Example exploit:
    username: admin' --
    password: anything
    
    This creates query: SELECT * FROM users WHERE username = 'admin' --' AND password = '...'
    The -- comments out the password check, bypassing authentication!
    """
    
    # VULNERABLE: Direct string concatenation in SQL query
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    
    print(f"[DEBUG] Executing query: {query}")
    
    try:
        # Executes the raw SQL query
        result = db.execute(text(query))
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

# VULNERABLE ENDPOINT #2: Get User by ID (also vulnerable)

@app.get("/get-user-vulnerable")
def get_user_vulnerable(user_id: str, db: Session = Depends(get_db)):
    """
    VULNERABLE endpoint - SQL Injection in ID parameter
    
    Even though user_id is typically a number, we accept it as string
    and concatenate directly into SQL query
    
    Example exploit:
    user_id: 1 OR 1=1
    
    This creates: SELECT * FROM users WHERE id = 1 OR 1=1
    1=1 is always true, so it returns ALL users!
    """
    
    # VULNERABLE: Direct string concatenation with user input
    query = f"SELECT * FROM users WHERE id = {user_id}"
    
    print(f"[DEBUG] Executing query: {query}")
    
    try:
        result = db.execute(text(query))
        users = result.fetchall()
        
        if users:
            return {
                "success": True,
                "users": [
                    {
                        "id": user[0],
                        "username": user[1],
                        "email": user[3]
                    }
                    for user in users
                ]
            }
        else:
            return {
                "success": False,
                "message": "No users found"
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


# INFO ENDPOINT - List all users (for reference)


@app.get("/all-users")
def get_all_users(db: Session = Depends(get_db)):
    """
    Returns all users in the database
    (For testing/reference purposes only)
    """
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
        "message": "Vulnerable API is running",
        "status": "🚨 INTENTIONALLY VULNERABLE FOR EDUCATIONAL PURPOSES 🚨"
    }

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
