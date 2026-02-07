from typing import Dict, List, Optional
from app.models.decision import Decision, DecisionEvent

class DecisionStore:
    """
    Singleton In-Memory Store for Decisions and Events.
    Serves as the System of Record for the MVP.
    """
    _decisions: Dict[str, Decision] = {}
    _events: List[DecisionEvent] = []

    @classmethod
    def save_decision(cls, decision: Decision):
        """
        Upserts a decision into the store.
        """
        cls._decisions[decision.id] = decision

    @classmethod
    def get_decision(cls, decision_id: str) -> Optional[Decision]:
        """
        Retrieves a decision by ID.
        """
        return cls._decisions.get(decision_id)

    @classmethod
    def get_all_decisions(cls) -> List[Decision]:
        """
        Returns all decisions.
        """
        return list(cls._decisions.values())

    @classmethod
    def log_event(cls, event: DecisionEvent):
        """
        Appends an immutable audit log entry.
        """
        cls._events.append(event)

    @classmethod
    def get_events_for_decision(cls, decision_id: str) -> List[DecisionEvent]:
        """
        Returns the audit trail for a specific decision.
        """
        return [e for e in cls._events if e.decision_id == decision_id]

    @classmethod
    def clear(cls):
        """
        Resets the store (useful for testing/re-upload).
        """
        cls._decisions.clear()
        cls._events.clear()
