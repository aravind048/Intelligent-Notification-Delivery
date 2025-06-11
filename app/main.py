# app/main.py

from fastapi import FastAPI
from app.routes import users, notifications
from app.database import Base, engine
import app.models  # ensures models are registered

# Create DB tables (only if they don’t exist)
Base.metadata.create_all(bind=engine)

# Initialize FastAPI
app = FastAPI()

# Include routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
