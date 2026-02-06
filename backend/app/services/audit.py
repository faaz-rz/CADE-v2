from datetime import datetime
from typing import List, Dict, Any
from app.models.decision import Decision, DecisionStatus

class AuditLogEntry:
    def __init__(self, decision_id: str, action: str, details: str):
        self.timestamp = datetime.now()
        self.decision_id = decision_id
        self.action = action
        self.details = details

# Simple in-memory storage for v1. In production, this would be a DB table.
_audit_log: List[AuditLogEntry] = []

class AuditService:
    @staticmethod
    def log_action(decision_id: str, action: str, details: str = ""):
        """
        Log a significant action related to a decision.
        """
        entry = AuditLogEntry(decision_id, action, details)
        _audit_log.append(entry)
        print(f"[AUDIT] {entry.timestamp} | {decision_id} | {action} | {details}")

    @staticmethod
    def get_logs_for_decision(decision_id: str) -> List[Dict[str, Any]]:
        return [
            {
                "timestamp": entry.timestamp,
                "action": entry.action,
                "details": entry.details
            }
            for entry in _audit_log
            if entry.decision_id == decision_id
        ]

    @staticmethod
    def log_approval(decision: Decision):
        AuditService.log_action(
            decision.id, 
            "APPROVED", 
            f"Approved decision for {decision.entity}. Estimated impact: {decision.expected_monthly_impact}"
        )

    @staticmethod
    def log_rejection(decision: Decision, reason: str):
        AuditService.log_action(
            decision.id, 
            "REJECTED", 
            f"Rejected decision for {decision.entity}. Reason: {reason}"
        )
