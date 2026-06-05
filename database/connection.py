from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = (
    f"sqlite:///{BASE_DIR / 'database' / 'predictive_maintenance.db'}"
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()