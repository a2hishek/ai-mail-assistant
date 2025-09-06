from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
#import sqlite3
from pathlib import Path
from config import DB_PATH
from models import Base


Path("data").mkdir(exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
SessionLocal = sessionmaker(bind=engine, future=True)

# def exec_script(path="schema.sql"):
#     with engine.connect() as conn:
#         with open(path, "r", encoding="utf-8") as f:
#             conn.execute(text(f.read()))
#         conn.commit()

# def exec_script(path="schema.sql"):
#     # Use sqlite3 directly because it supports executescript
#     with sqlite3.connect(DB_PATH) as conn:
#         with open(path, "r", encoding="utf-8") as f:
#             conn.executescript(f.read())

Base.metadata.create_all(engine)