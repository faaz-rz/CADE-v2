
import sys
import uuid
from app.services.decision_store import DecisionStore
from app.models.decision import Decision, DecisionStatus, DecisionType, DecisionScope, ImpactLabel, RiskLevel, DecisionContext, DecisionEventType
from app.api.decisions import approve_decision, reject_decision, defer_decision, ReviewNote
from fastapi import HTTPException

def create_mock_decision():
    return Decision(
        id=str(uuid.uuid4()),
        decision_type=DecisionType.VENDOR_REDUCE,
        scope=DecisionScope.VENDOR,
        entity="TestVendor",
        recommended_action="Reduce Spend",
        explanation="Test Explanation",
        context=DecisionContext(
            analysis_period="Test",
            rule_id="TEST_RULE",
            thresholds={},
            metrics={}
        ),
        expected_monthly_impact=100.0,
        cost_of_inaction=1200.0,
        annual_impact=1200.0,
        impact_label=ImpactLabel.LOW,
        risk_level=RiskLevel.LOW,
        risk_range={"best_case": 1200.0, "worst_case": 0},
        confidence=0.9
    )

def run_test():
    print("Running Decision Lifecycle Test...")
    DecisionStore.clear()

    # 1. Test Happy Path: Approve
    print("\n[Test 1] PENDING -> APPROVED")
    d1 = create_mock_decision()
    DecisionStore.save_decision(d1)
    
    updated_d1 = approve_decision(d1.id, ReviewNote(note="Looks good"))
    
    if updated_d1.status != DecisionStatus.APPROVED:
        print(f"FAIL: Expected APPROVED, got {updated_d1.status}")
        sys.exit(1)
        
    events = DecisionStore.get_events_for_decision(d1.id)
    if len(events) != 1 or events[0].event_type != DecisionEventType.APPROVED:
        print(f"FAIL: Event log mismatch. {events}")
        sys.exit(1)
    print("PASS")

    # 2. Test Invalid Transition: Approve -> Reject
    print("\n[Test 2] APPROVED -> REJECTED (Should Fail)")
    try:
        reject_decision(d1.id, ReviewNote(note="Changed my mind"))
        print("FAIL: Should have raised HTTPException")
        sys.exit(1)
    except HTTPException as e:
        if e.status_code != 400:
            print(f"FAIL: Expected 400, got {e.status_code}")
            sys.exit(1)
        print("PASS (Blocked as expected)")

    # 3. Test Deferral Flow: PENDING -> DEFERRED -> REJECTED
    print("\n[Test 3] PENDING -> DEFERRED -> REJECTED")
    d2 = create_mock_decision()
    DecisionStore.save_decision(d2)
    
    # Defer
    defer_decision(d2.id, ReviewNote(note="Wait for Q3"))
    if DecisionStore.get_decision(d2.id).status != DecisionStatus.DEFERRED:
        print("FAIL: Deferral failed")
        sys.exit(1)
        
    # Reject (from Deferred)
    reject_decision(d2.id, ReviewNote(note="Actually no"))
    final_d2 = DecisionStore.get_decision(d2.id)
    if final_d2.status != DecisionStatus.REJECTED:
        print(f"FAIL: Expected REJECTED, got {final_d2.status}")
        sys.exit(1)
        
    events = DecisionStore.get_events_for_decision(d2.id)
    if len(events) != 2: # Deferred, then Rejected
        print(f"FAIL: Expected 2 events, got {len(events)}")
        sys.exit(1)
    print("PASS")

    print("\nAll Lifecycle Tests Passed!")

if __name__ == "__main__":
    run_test()
