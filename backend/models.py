from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    yarns = relationship("YarnStash", back_populates="owner", cascade="all, delete-orphan")
    saved_patterns = relationship("SavedPattern", back_populates="user", cascade="all, delete-orphan")


class YarnStash(Base):
    __tablename__ = "yarn_stash"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    brand = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    material = Column(String(100), nullable=False)
    diameter_mm = Column(Float, nullable=False)          # Diamètre du fil en mm (ex: 3.0, 6.0)
    color_hex = Column(String(7), nullable=False)        # ex: #D96B43
    remaining_grams = Column(Integer, nullable=False)    # Poids restant pesé
    remaining_meters = Column(Integer, nullable=False)   # Métrage estimé
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="yarns")


class SavedPattern(Base):
    __tablename__ = "saved_patterns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    ravelry_pattern_id = Column(Integer, nullable=False)
    pattern_name = Column(String(150), nullable=False)
    status = Column(String(50), default="saved")

    user = relationship("User", back_populates="saved_patterns")