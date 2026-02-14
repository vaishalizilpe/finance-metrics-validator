from pydantic import BaseModel, Field
from typing import List, Literal, Optional

RiskLevel = Literal["low", "medium", "high"]

class Finding(BaseModel):
    code: str
    severity: RiskLevel
    message: str
    evidence: Optional[str] = None

class ReconciliationResult(BaseModel):
    ledger_total: float
    model_total: float
    delta: float
    delta_pct: float
    within_tolerance: bool
    tolerance_pct: float

class Report(BaseModel):
    model_name: str
    findings: List[Finding] = Field(default_factory=list)
    reconciliation: Optional[ReconciliationResult] = None