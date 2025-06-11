from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class NotificationChannel(str, enum.Enum):
    email = "email"
    sms = "sms"
    push = "push"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    preferred_channel = Column(Enum(NotificationChannel), default="email")
    dnd_start = Column(String, nullable=True)  # e.g., "22:00"
    dnd_end = Column(String, nullable=True)    # e.g., "07:00"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    logs = relationship("ActivityLog", back_populates="user")
    notifications = relationship("NotificationLog", back_populates="user")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(String(50), nullable=False)
    metadata = Column(Text)  # optional raw JSON/text
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="logs")


class NotificationRule(Base):
    __tablename__ = "notification_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    event_type = Column(String(50), nullable=False)
    trigger_condition = Column(String, nullable=False)  # e.g., "count >= 3"
    time_window_minutes = Column(Integer, nullable=True)  # optional
    message_template = Column(Text)
    channel = Column(Enum(NotificationChannel), default="email")
    priority = Column(String, default="normal")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    rule_id = Column(Integer, ForeignKey("notification_rules.id"), nullable=True)
    message = Column(Text, nullable=False)
    channel = Column(Enum(NotificationChannel), default="email")
    status = Column(String, default="sent")  # sent, failed, queued, retried
    attempts = Column(Integer, default=0)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="notifications")


class RetryQueue(Base):
    __tablename__ = "retry_queue"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notification_logs.id"))
    next_attempt_at = Column(DateTime(timezone=True))
    retries_left = Column(Integer, default=3)
    status = Column(String, default="pending")
