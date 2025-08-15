

#Base = declarative_base()  


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# 1. Create the engine
engine = create_engine(settings.DATABASE_URL, echo=False)

# 2. Create a configured “Session” class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Base class for ORM models
Base = declarative_base()

