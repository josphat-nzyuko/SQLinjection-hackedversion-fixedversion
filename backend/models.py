
 
from sqlalchemy import Column, Integer, String
from database import Base
 
"""
the code below tells SQL Alchemy to create a 'users' table with the specified columns when i call Base.metadata.create_all()
"""
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    email = Column(String)
 
