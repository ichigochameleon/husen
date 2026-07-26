from sqlmodel import Session, SQLModel, create_engine, select
from pathlib import Path

sqlite_file_name = "banana.db"
BASE_DIR = Path(__file__).resolve().parent
sqlite_url = f"sqlite:///{BASE_DIR /'banana.db'}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session