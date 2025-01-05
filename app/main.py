from fastapi import FastAPI
from app.database import Base, engine
from app.routers import urls
from app.middleware.rate_limiter import RateLimitMiddleware
from app.schedular import start_cleanup_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener Service")

app.add_middleware(RateLimitMiddleware, limit=100, window=60) 

app.include_router(urls.router)

start_cleanup_scheduler()