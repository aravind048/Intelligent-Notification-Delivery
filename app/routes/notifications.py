# app/routes/notifications.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, time
from typing import List

from app import models, schemas, database, auth

router = APIRouter()


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Utility: Check if in DND time
# -----------------------------
def is_within_dnd(dnd_start: str, dnd_end: str) -> bool:
    now = datetime.now().time()
    start = datetime.strptime(dnd_start, "%H:%M").time()
    end = datetime.strptime(dnd_end, "%H:%M").time()

    if start < end:
        return start <= now < end
    else:  # DND wraps around midnight
        return now >= start or now < end


# -----------------------------
# POST /notifications/notify
# -----------------------------
@router.post("/notify", status_code=201)
def send_notification(
    payload: schemas.NotificationSend,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check DND window
    if user.dnd_start and user.dnd_end and is_within_dnd(user.dnd_start, user.dnd_end):
        raise HTTPException(status_code=403, detail="User is in Do Not Disturb hours")

    # Create log entry
    log = models.NotificationLog(
        user_id=payload.user_id,
        message=payload.message,
        channel=payload.channel,
        status="sent",  # Assume success, change later if failed
        attempts=1,
        rule_id=None  # Optional: attach rule ID if triggered by rule
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    # Simulate dispatch (replace with Celery task later)
    print(f"[{datetime.now()}] Sending {payload.channel.upper()} to User {payload.user_id}: {payload.message}")

    return {"message": "Notification sent", "log_id": log.id}


# -----------------------------
# GET /notifications/logs
# -----------------------------
@router.get("/logs", response_model=List[schemas.NotificationLogOut])
def get_logs(
    user_id: int = None,
    status: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    query = db.query(models.NotificationLog)

    if user_id:
        query = query.filter(models.NotificationLog.user_id == user_id)
    if status:
        query = query.filter(models.NotificationLog.status == status)

    return query.order_by(models.NotificationLog.sent_at.desc()).all()
