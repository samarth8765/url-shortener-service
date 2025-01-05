from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.services import cleanup_expired_urls

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def start_cleanup_scheduler():
    scheduler = BackgroundScheduler()

    def scheduled_cleanup():
        db = SessionLocal()
        try:
            cleanup_expired_urls(db)
        finally:
            db.close()

    scheduler.add_job(scheduled_cleanup, "interval", hours=1)  
    scheduler.start()
    print("Scheduler started: Cleanup task will run every hour.")
