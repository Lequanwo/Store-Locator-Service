import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# for deployment, DATABASE_URL must be set in environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# for testing
if not DATABASE_URL:
    print("⚠️  DATABASE_URL not set in environment variables. Using default local database URL.  ")
    DATABASE_URL = "postgresql://postgres:2222@localhost:5432/store_locator"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()