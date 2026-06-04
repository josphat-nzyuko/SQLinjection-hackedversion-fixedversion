from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool
 
# SQLite database file location
DATABASE_URL = "sqlite:///./vulnerable_app.db"
 
# Creates a SQLAlchemy engine
# StaticPool keeps the connection open (good for SQLite in testing)
# check_same_thread=False allows multiple threads (needed for Uvicorn)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
 
# Creation of session factory - this will be used to create database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
 
# Base class - all ORM models inherit from this
Base = declarative_base()
 
def get_db():
    """
    Dependency function for FastAPI
    Creates a new database session for each request
    Usage in app.py: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()