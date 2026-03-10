"""
Decision Store — Dual-mode storage (in-memory + SQLite).

Maintains backward-compatible public API while adding persistent DB storage.
In-memory store is kept as a fast cache; DB is the source of truth.
"""

import json
from typing import Dict, List, Optional
from app.models.decision import Decision, DecisionEvent


class DecisionStore:
    """
    System of Record for Decisions and Events.
    Uses in-memory cache with SQLite write-through persistence.
    """
    _decisions: Dict[str, Decision] = {}
    _events: List[DecisionEvent] = []
    _db_enabled: bool = False

    @classmethod
    def enable_db(cls):
        """Enable database persistence. Called at app startup."""
        cls._db_enabled = True

    @classmethod
    def save_decision(cls, decision: Decision):
        """Upserts a decision into both cache and DB."""
        cls._decisions[decision.id] = decision

        if cls._db_enabled:
            cls._persist_decision_to_db(decision)

    @classmethod
    def get_decision(cls, decision_id: str) -> Optional[Decision]:
        """Retrieves a decision by ID."""
        return cls._decisions.get(decision_id)

    @classmethod
    def get_all_decisions(cls) -> List[Decision]:
        """Returns all decisions."""
        return list(cls._decisions.values())

    @classmethod
    def log_event(cls, event: DecisionEvent):
        """Appends an immutable audit log entry."""
        cls._events.append(event)

        if cls._db_enabled:
            cls._persist_event_to_db(event)

    @classmethod
    def get_events_for_decision(cls, decision_id: str) -> List[DecisionEvent]:
        """Returns the audit trail for a specific decision."""
        return [e for e in cls._events if e.decision_id == decision_id]

    @classmethod
    def clear(cls):
        """Resets the in-memory store (useful for testing/re-upload) and DB."""
        cls._decisions.clear()
        cls._events.clear()
        
        if cls._db_enabled:
            try:
                from app.db.database import SessionLocal
                from sqlalchemy import text
                db = SessionLocal()
                try:
                    db.execute(text("DELETE FROM decision_events"))
                    db.execute(text("DELETE FROM decisions"))
                    db.commit()
                finally:
                    db.close()
            except Exception as e:
                print(f"[DecisionStore] DB clear failed: {e}")

    @classmethod
    def load_from_db(cls):
        """Load all decisions and events from DB into cache at startup."""
        if not cls._db_enabled:
            return

        try:
            from app.db.database import SessionLocal
            from app.db.db_models import DecisionTable, DecisionEventTable
            from app.models.decision import (
                DecisionType, DecisionScope, DecisionStatus,
                RiskLevel, ImpactLabel, DecisionContext,
                DecisionEventType,
            )

            db = SessionLocal()
            try:
                rows = db.query(DecisionTable).all()
                for row in rows:
                    context_data = json.loads(row.context_json) if row.context_json else None
                    context = DecisionContext(**context_data) if context_data else None

                    import re
                    if re.match(r"^Vendor_\d+$", row.entity):
                        continue

                    risk_range = json.loads(row.risk_range_json) if row.risk_range_json else {"best_case": 0, "worst_case": 0}

                    decision = Decision(
                        id=row.id,
                        decision_type=DecisionType(row.decision_type),
                        scope=DecisionScope(row.scope),
                        entity=row.entity,
                        recommended_action=row.recommendation,
                        explanation=row.explanation or "",
                        context=context,
                        expected_monthly_impact=row.expected_monthly_impact,
                        cost_of_inaction=row.cost_of_inaction,
                        annual_impact=row.annual_impact,
                        impact_label=ImpactLabel(row.impact_label),
                        risk_level=RiskLevel(row.risk_level),
                        risk_score=row.risk_score,
                        risk_range=risk_range,
                        confidence=row.confidence,
                        status=DecisionStatus(row.status),
                        created_at=row.created_at,
                        updated_at=row.updated_at,
                    )
                    cls._decisions[decision.id] = decision

                event_rows = db.query(DecisionEventTable).order_by(DecisionEventTable.timestamp).all()
                for erow in event_rows:
                    event = DecisionEvent(
                        id=erow.id,
                        decision_id=erow.decision_id,
                        event_type=DecisionEventType(erow.event_type),
                        previous_status=DecisionStatus(erow.previous_status) if erow.previous_status else None,
                        new_status=DecisionStatus(erow.new_status),
                        actor_id=erow.actor,
                        note=erow.note,
                        created_at=erow.timestamp,
                    )
                    cls._events.append(event)
            finally:
                db.close()
        except Exception as e:
            print(f"[DecisionStore] Failed to load from DB: {e}")

    @classmethod
    def _persist_decision_to_db(cls, decision: Decision):
        """Write-through: persist decision to SQLite."""
        try:
            from app.db.database import SessionLocal
            from app.db.db_models import DecisionTable

            db = SessionLocal()
            try:
                context_json = json.dumps(decision.context.model_dump()) if decision.context else None
                risk_range_json = json.dumps(decision.risk_range)

                existing = db.query(DecisionTable).filter(DecisionTable.id == decision.id).first()
                if existing:
                    existing.status = decision.status.value
                    existing.updated_at = decision.updated_at
                    existing.risk_level = decision.risk_level.value
                    existing.risk_score = decision.risk_score
                    existing.context_json = context_json
                else:
                    row = DecisionTable(
                        id=decision.id,
                        entity=decision.entity,
                        decision_type=decision.decision_type.value,
                        scope=decision.scope.value,
                        recommendation=decision.recommended_action,
                        explanation=decision.explanation,
                        financial_impact=decision.annual_impact,
                        annual_impact=decision.annual_impact,
                        expected_monthly_impact=decision.expected_monthly_impact,
                        cost_of_inaction=decision.cost_of_inaction,
                        impact_label=decision.impact_label.value,
                        risk_level=decision.risk_level.value,
                        risk_score=decision.risk_score,
                        confidence=decision.confidence,
                        status=decision.status.value,
                        context_json=context_json,
                        risk_range_json=risk_range_json,
                        created_at=decision.created_at,
                        updated_at=decision.updated_at,
                    )
                    db.add(row)
                db.commit()
            finally:
                db.close()
        except Exception as e:
            print(f"[DecisionStore] DB persist failed: {e}")

    @classmethod
    def _persist_event_to_db(cls, event: DecisionEvent):
        """Write-through: persist event to SQLite (append-only)."""
        try:
            from app.db.database import SessionLocal
            from app.db.db_models import DecisionEventTable

            db = SessionLocal()
            try:
                row = DecisionEventTable(
                    id=event.id,
                    decision_id=event.decision_id,
                    event_type=event.event_type.value,
                    previous_status=event.previous_status.value if event.previous_status else None,
                    new_status=event.new_status.value,
                    actor=event.actor_id,
                    note=event.note,
                    timestamp=event.created_at,
                )
                db.add(row)
                db.commit()
            finally:
                db.close()
        except Exception as e:
            print(f"[DecisionStore] Event persist failed: {e}")
