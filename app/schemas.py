from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum
from datetime import datetime


# --- Enum for notification channel ---
class NotificationChannel(str, Enum):
    email = "email"
    sms = "sms"
    push = "push"


# --- Auth Schemas ---
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    preferred_channel: Optional[NotificationChannel] = "email"
    dnd_start: Optional[str] = None  # e.g., "22:00"
    dnd_end: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- User Info Response ---
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    preferred_channel: NotificationChannel
    dnd_start: Optional[str]
    dnd_end: Optional[str]

    class Config:
        orm_mode = True


# --- Activity Log ---
class ActivityLogIn(BaseModel):
    user_id: int
    event_type: str
    event_metadata: Optional[str] = None


class ActivityLogOut(BaseModel):
    id: int
    user_id: int
    event_type: str
    event_metadata: Optional[str]
    timestamp: datetime

    class Config:
        orm_mode = True


# --- Notification Rule ---
class RuleCreate(BaseModel):
    name: str
    event_type: str
    trigger_condition: str
    time_window_minutes: Optional[int] = None
    message_template: str
    channel: NotificationChannel
    priority: Optional[str] = "normal"
    active: Optional[bool] = True


# --- Notification ---
class NotificationSend(BaseModel):
    user_id: int
    message: str
    channel: NotificationChannel
    priority: Optional[str] = "normal"


class NotificationLogOut(BaseModel):
    id: int
    user_id: int
    message: str
    channel: NotificationChannel
    status: str
    attempts: int
    sent_at: datetime

    class Config:
        orm_mode = True
