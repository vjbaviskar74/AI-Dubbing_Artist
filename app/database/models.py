from sqlalchemy import Column, Integer, String, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.connection import Base
from datetime import datetime

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, index=True)
    video_path = Column(String)
    source_language = Column(String)
    target_language = Column(String)
    consent_verified = Column(Boolean, default=False)
    status = Column(String, default="pending")
    mode = Column(String, default="mvp")
    created_at = Column(String, default=lambda: datetime.now().isoformat())

    # Metadata relations (simplified for MVP)
    genre = Column(String)
    scene_mood = Column(String)
    humor_type = Column(String)
    overall_score = Column(Float)
    
class Segment(Base):
    __tablename__ = "segments"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"))
    segment_id = Column(String)
    speaker_id = Column(String)
    start_time = Column(Float)
    end_time = Column(Float)
    original_text = Column(Text)
    translated_text = Column(Text)
    adapted_text = Column(Text)
    emotion = Column(String)
    humor_type = Column(String)
    audio_path = Column(String)
