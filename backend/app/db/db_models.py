"""
SQLAlchemy ORM Models — Tables for persistent storage.

Tables:
- vendors: Vendor master data
- decisions: Decision records with lifecycle state
- decision_events: Immutable append-only audit log
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.database import Base


class VendorTable(Base):
    __tablename__ = "vendors"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False, default="Uncategorized")
    total_spend = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    decisions = relationship("DecisionTable", back_populates="vendor")


class DecisionTable(Base):
    __tablename__ = "decisions"

    id = Column(String, primary_key=True)
    vendor_id = Column(String, ForeignKey("vendors.id"), nullable=True)
    entity = Column(String, nullable=False)
    decision_type = Column(String, nullable=False)
    scope = Column(String, nullable=False)
    recommendation = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    financial_impact = Column(Float, nullable=False, default=0.0)
    annual_impact = Column(Float, nullable=False, default=0.0)
    expected_monthly_impact = Column(Float, nullable=False, default=0.0)
    cost_of_inaction = Column(Float, nullable=False, default=0.0)
    impact_label = Column(String, nullable=False, default="LOW")
    risk_level = Column(String, nullable=False, default="LOW")
    risk_score = Column(Integer, nullable=False, default=0)
    confidence = Column(Float, nullable=False, default=0.0)
    status = Column(String, nullable=False, default="PENDING")
    context_json = Column(Text, nullable=True)  # Serialized DecisionContext
    risk_range_json = Column(Text, nullable=True)  # Serialized risk_range dict
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    vendor = relationship("VendorTable", back_populates="decisions")
    events = relationship("DecisionEventTable", back_populates="decision", order_by="DecisionEventTable.timestamp")


class DecisionEventTable(Base):
    """
    Immutable audit log — append-only, no UPDATE or DELETE.
    """
    __tablename__ = "decision_events"

    id = Column(String, primary_key=True)
    decision_id = Column(String, ForeignKey("decisions.id"), nullable=False)
    event_type = Column(String, nullable=False)
    previous_status = Column(String, nullable=True)
    new_status = Column(String, nullable=False)
    actor = Column(String, nullable=False, default="system")
    note = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    decision = relationship("DecisionTable", back_populates="events")
