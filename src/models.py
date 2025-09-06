from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Email(Base):
    __tablename__ = "emails"

    id = Column(String(9), primary_key=True)
    sender = Column(String(255), nullable=False)
    subject = Column(Text, nullable=True)
    body = Column(Text, nullable=True)
    date_received = Column(DateTime, nullable=True)
    support = Column(String(50), default="No")
    priority = Column(String(50), default="Not urgent")
    sentiment = Column(String(50), default="Neutral")
    status = Column(String(50), default="pending")
    draft_reply = Column(Text, nullable=True)
    date_sent = Column(DateTime, nullable=True) 

class KBDoc(Base):
    __tablename__ = "kb_docs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
