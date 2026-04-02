import json
from datetime import datetime
from app.db.database import SessionLocal
from app.db.db_models import SimulationSnapshot

class SimulationStore:
    
    @staticmethod
    def save_snapshot(
        vendor_id: str,
        snapshot_type: str,
        parameters: dict,
        result: dict,
        decision_id: str | None = None
    ) -> int:
        db = SessionLocal()
        try:
            snapshot = SimulationSnapshot(
                vendor_id=vendor_id,
                snapshot_type=snapshot_type,
                parameters=json.dumps(parameters),
                result=json.dumps(result, default=str),
                decision_id=decision_id,
            )
            db.add(snapshot)
            db.commit()
            db.refresh(snapshot)
            return snapshot.id
        finally:
            db.close()
    
    @staticmethod
    def get_latest_for_vendor(
        vendor_id: str,
        snapshot_type: str | None = None
    ) -> dict | None:
        db = SessionLocal()
        try:
            query = db.query(SimulationSnapshot).filter(SimulationSnapshot.vendor_id == vendor_id)
            if snapshot_type:
                query = query.filter(SimulationSnapshot.snapshot_type == snapshot_type)
            
            snapshot = query.order_by(SimulationSnapshot.created_at.desc()).first()
            if not snapshot:
                return None
            return {
                "id": snapshot.id,
                "vendor_id": snapshot.vendor_id,
                "snapshot_type": snapshot.snapshot_type,
                "parameters": json.loads(snapshot.parameters),
                "result": json.loads(snapshot.result),
                "decision_id": snapshot.decision_id,
                "created_at": snapshot.created_at.isoformat(),
            }
        finally:
            db.close()
    
    @staticmethod
    def get_latest_portfolio() -> dict | None:
        db = SessionLocal()
        try:
            snapshot = db.query(SimulationSnapshot)\
                .filter(SimulationSnapshot.snapshot_type == "portfolio_mc")\
                .order_by(SimulationSnapshot.created_at.desc())\
                .first()
            if not snapshot:
                return None
            return {
                "id": snapshot.id,
                "parameters": json.loads(snapshot.parameters),
                "result": json.loads(snapshot.result),
                "created_at": snapshot.created_at.isoformat(),
            }
        finally:
            db.close()
    
    @staticmethod
    def get_for_decision(decision_id: str) -> list[dict]:
        db = SessionLocal()
        try:
            snapshots = db.query(SimulationSnapshot)\
                .filter(SimulationSnapshot.decision_id == decision_id)\
                .order_by(SimulationSnapshot.created_at.desc())\
                .all()
            return [
                {
                    "id": s.id,
                    "snapshot_type": s.snapshot_type,
                    "parameters": json.loads(s.parameters),
                    "result": json.loads(s.result),
                    "created_at": s.created_at.isoformat(),
                }
                for s in snapshots
            ]
        finally:
            db.close()
    
    @staticmethod
    def get_all_latest_vendor_snapshots() -> dict[str, dict]:
        db = SessionLocal()
        try:
            from sqlalchemy import func
            subq = db.query(
                SimulationSnapshot.vendor_id,
                func.max(SimulationSnapshot.created_at).label("max_date")
            ).group_by(SimulationSnapshot.vendor_id).subquery()
            
            snapshots = db.query(SimulationSnapshot).join(
                subq,
                (SimulationSnapshot.vendor_id == subq.c.vendor_id) &
                (SimulationSnapshot.created_at == subq.c.max_date)
            ).all()
            
            return {
                s.vendor_id: {
                    "snapshot_type": s.snapshot_type,
                    "parameters": json.loads(s.parameters),
                    "result": json.loads(s.result),
                    "created_at": s.created_at.isoformat(),
                }
                for s in snapshots
            }
        finally:
            db.close()
