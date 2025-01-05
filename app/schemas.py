from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class URLCreate(BaseModel):
    original_url: str
    expires_at: Optional[datetime] = None

class URLResponse(BaseModel):
    original_url: str
    short_url: str
    created_at: datetime
    expires_at: Optional[datetime]
    expired: bool
    access_count: int
