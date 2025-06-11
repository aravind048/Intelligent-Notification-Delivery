from app.database import Base, engine
import app.models  # Make sure to import models so Base is aware

Base.metadata.create_all(bind=engine)
