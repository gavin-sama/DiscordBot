from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel
from typing import List, Optional
from fastapi import HTTPException

# Create a FastAPI instance
app = FastAPI()

DATABASE_URL = "sqlite:///./music_info.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class GenreDB(Base):
    __tablename__ = "Genre"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Genre(BaseModel):
    id: Optional[int] = None
    name: str
    description: str



# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the music genre info FastAPI!"}

# Get genre endpoint
@app.get("/genre/{genre_name}", response_model=Genre)
def get_genre_description(genre_name: str, db: Session = Depends(get_db)):
    
    genre = db.query(GenreDB).filter(GenreDB.name == genre_name).first()

    # Error handling
    if not genre:
        raise HTTPException(status_code=404, detail="Genre not found")
    
    # Return the genre description
    return genre
