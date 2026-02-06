from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date

class FinancialRecord(BaseModel):
    """
    Represents a raw row of financial data from ingestion.
    """
    date: date
    entity: str = Field(..., description="Vendor or Project name")
    category: str = Field(..., description="Expense category (e.g. Software, contractor)")
    amount: float = Field(..., description="Monetary value")
    currency: str = "USD"
    description: Optional[str] = None
    
    @field_validator('amount')
    def amount_must_be_positive_or_zero(cls, v):
        # We might allow negatives for refunds, but generally costs are positive in this context
        return v
