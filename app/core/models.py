

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base  # Base = declarative_base() in db.py

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    block = Column(String, nullable=False)
    # one-to-many to interactions and feedback
    interactions = relationship("Interaction", back_populates="user")
    feedback_logs = relationship("FeedbackLog", back_populates="user")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    community = Column(String, nullable=False, index=True)
    created_at = Column(DateTime)
    # one-to-many to interactions and feedback
    interactions = relationship("Interaction", back_populates="item")
    feedback_logs = relationship("FeedbackLog", back_populates="item")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    interaction_type = Column(String, nullable=False)  # e.g., "view", "click"
    timestamp = Column(DateTime)

    # define backrefs to user and item
    user = relationship("User", back_populates="interactions")
    item = relationship("Item", back_populates="interactions")


class FeedbackLog(Base):
    __tablename__ = "feedback_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    feedback_type = Column(String, nullable=False)  # e.g., "like", "hide"
    timestamp = Column(DateTime)

    user = relationship("User", back_populates="feedback_logs")
    item = relationship("Item", back_populates="feedback_logs")
