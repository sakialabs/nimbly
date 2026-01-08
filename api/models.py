"""
SQLAlchemy ORM models for Nimbly
"""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Integer, Enum, Date, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from api.database import Base

class ParseStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    receipts = relationship("Receipt", back_populates="user", cascade="all, delete-orphan")

class Store(Base):
    __tablename__ = "stores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    normalized_name = Column(String, unique=True, nullable=False, index=True)
    address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    receipts = relationship("Receipt", back_populates="store")
    price_history = relationship("PriceHistory", back_populates="store")

class Receipt(Base):
    __tablename__ = "receipts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=True, index=True)
    upload_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    purchase_date = Column(Date, nullable=True, index=True)
    total_amount = Column(Numeric(10, 2), nullable=True)
    original_file_path = Column(String, nullable=False)
    parse_status = Column(Enum(ParseStatus), default=ParseStatus.PENDING, nullable=False)
    parse_error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="receipts")
    store = relationship("Store", back_populates="receipts")
    line_items = relationship("LineItem", back_populates="receipt", cascade="all, delete-orphan")

class LineItem(Base):
    __tablename__ = "line_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipts.id"), nullable=False, index=True)
    product_name = Column(String, nullable=False)
    normalized_product_name = Column(String, nullable=False, index=True)
    quantity = Column(Numeric(10, 2), nullable=True)
    unit_price = Column(Numeric(10, 2), nullable=True)
    total_price = Column(Numeric(10, 2), nullable=False)
    line_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    receipt = relationship("Receipt", back_populates="line_items")
    price_history = relationship("PriceHistory", back_populates="source_line_item")

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_name = Column(String, nullable=False, index=True)
    store_id = Column(UUID(as_uuid=True), ForeignKey("stores.id"), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    observed_date = Column(Date, nullable=False, index=True)
    source_line_item_id = Column(UUID(as_uuid=True), ForeignKey("line_items.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    store = relationship("Store", back_populates="price_history")
    source_line_item = relationship("LineItem", back_populates="price_history")
    
    # Composite indexes for efficient queries
    __table_args__ = (
        {'extend_existing': True}
    )
