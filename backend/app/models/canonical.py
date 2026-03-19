from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional

class CanonicalFinancialRecord(BaseModel):
    """
    The Single Source of Truth for the Decision Engine.
    All external data MUST be transformed into this format before hitting business logic.
    """
    date: date
    amount: float = Field(..., description="Monetary value in normalized base currency")
    category: str = Field(..., description="Normalized expense category")
    entity: str = Field(..., description="Vendor, Project, or Department name")
    currency: str = Field(default="USD", description="ISO currency code")
    gl_code: Optional[str] = None
    cost_center: Optional[str] = None
    po_number: Optional[str] = None
    description: Optional[str] = None
    source_file: str = Field(..., description="Origin filename for audit trails")

    @field_validator('amount')
    def amount_must_be_valid(cls, v):
        # We allow negatives for refunds/adjustments, but warn if 0
        if v == 0:
            raise ValueError("Transaction amount cannot be zero")
        return v
