from sqlalchemy.orm import Session
from app.database.models import Job, Segment

def create_job(db: Session, job_id: str, video_path: str, source_lang: str, target_lang: str, consent: bool):
    db_job = Job(id=job_id, video_path=video_path, source_language=source_lang, target_language=target_lang, consent_verified=consent)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_job(db: Session, job_id: str):
    return db.query(Job).filter(Job.id == job_id).first()

def update_job_status(db: Session, job_id: str, status: str):
    job = get_job(db, job_id)
    if job:
        job.status = status
        db.commit()
        db.refresh(job)
    return job

def create_segment(db: Session, job_id: str, segment_id: str, start: float, end: float, text: str):
    db_seg = Segment(job_id=job_id, segment_id=segment_id, start_time=start, end_time=end, original_text=text)
    db.add(db_seg)
    db.commit()
    db.refresh(db_seg)
    return db_seg

def update_segment_translation(db: Session, seg_id: int, translation: str, adapted: str = None):
    seg = db.query(Segment).filter(Segment.id == seg_id).first()
    if seg:
        seg.translated_text = translation
        if adapted:
            seg.adapted_text = adapted
        db.commit()
        db.refresh(seg)
    return seg
