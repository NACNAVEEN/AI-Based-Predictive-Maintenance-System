import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.connection import engine
from database.models import Base

Base.metadata.create_all(bind=engine)

print("Tables Created Successfully")