"""
Database models and setup
"""
from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
import os

# Get DATABASE_URL from environment or use default
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///reviews.db')

Base = declarative_base()


class Review(Base):
    """Review model"""
    __tablename__ = 'reviews'

    review_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rating = Column(Integer, nullable=False)
    review_text = Column(Text, nullable=False)
    ai_summary = Column(Text, nullable=True)
    ai_recommended_actions = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'review_id': self.review_id,
            'rating': self.rating,
            'review_text': self.review_text,
            'ai_summary': self.ai_summary or '',
            'ai_recommended_actions': self.ai_recommended_actions or '',
            'created_at': self.created_at.isoformat() if self.created_at else ''
        }


# Database setup
# Fix connection pool issues for SQLite
if 'sqlite' in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={'check_same_thread': False},
        poolclass=None,  # Disable connection pooling for SQLite
        pool_pre_ping=True
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

