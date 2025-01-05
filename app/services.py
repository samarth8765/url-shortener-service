from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import URL
import hashlib
import redis
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),  
    port=int(os.getenv("REDIS_PORT", 6379)),  
    decode_responses=True
)
def generate_short_url(original_url: str) -> str:
    return hashlib.md5(original_url.encode()).hexdigest()[:7]

def create_short_url(db: Session, original_url: str, expires_at: datetime = None) -> URL:
    db_url = db.query(URL).filter(URL.original_url == original_url).first()
    if db_url:
        return db_url

    short_url = generate_short_url(original_url)
    if not expires_at:
        expires_at = datetime.utcnow() + timedelta(days=30)

    db_url = URL(
        original_url=original_url,
        short_url=short_url,
        created_at=datetime.utcnow(),
        expires_at=expires_at,
        expired=False,
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url

def get_original_url(db: Session, short_url: str) -> str:
    cached_url = redis_client.get(f"url:{short_url}")
    if cached_url:
        db_url = db.query(URL).filter(URL.short_url == short_url).first()
        if db_url:
            db_url.access_count += 1
            db.commit()
        return cached_url
    
    db_url = db.query(URL).filter(URL.short_url == short_url).first()
    if db_url and not db_url.expired:
        ttl = min(24 * 3600, int((db_url.expires_at - datetime.utcnow()).total_seconds()))
        redis_client.setex(f"url:{short_url}", ttl, db_url.original_url)

        db_url.access_count += 1
        db.commit()

        return db_url.original_url
    return None


def get_access_count(db: Session, short_url: str) -> int:
    db_url = db.query(URL).filter(URL.short_url == short_url).first()
    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return db_url.access_count, db_url.original_url, db_url.expires_at
    

def cleanup_expired_urls(db: Session):
    now = datetime.utcnow()

    expired_urls = db.query(URL).filter(URL.expires_at < now, URL.expired == False).all()

    for url in expired_urls:
        redis_client.delete(f"url:{url.short_url}")
        url.expired = True
        db.commit()

    print(f"Cleanup complete. Removed {len(expired_urls)} expired URLs.")
