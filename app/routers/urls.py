from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from app.database import get_db
from app.schemas import URLCreate, URLResponse
from app.services import create_short_url, get_access_count, get_original_url
from app.utils import is_reachable_url, is_valid_url

router = APIRouter()

@router.get("/ping")
def ping():
    return {"message": "pong"}

@router.post("/shorten", response_model=URLResponse)
def shorten_url(payload: URLCreate, db: Session = Depends(get_db)):
    # validate URL format
    if not is_valid_url(payload.original_url):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # check if the URL is reachable
    if not is_reachable_url(payload.original_url):
        raise HTTPException(status_code=400, detail="URL is not reachable")
    
    return create_short_url(db, payload.original_url, payload.expires_at)

@router.get("/{short_url}")
def redirect_to_original(short_url: str, db: Session = Depends(get_db)):
    original_url = get_original_url(db, short_url)
    if not original_url:
        raise HTTPException(status_code=404, detail="Short URL not found or expired")
    return RedirectResponse(original_url)

@router.get("/access_count/{short_url}")
def get_access_count_route(short_url: str, db: Session = Depends(get_db)):
    access_count, original_url, expires_at = get_access_count(db, short_url)
    if access_count is None:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return {"short_url": short_url, "access_count": access_count, "original_url": original_url, "expires_at": expires_at}
