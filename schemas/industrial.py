from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


ObservationClass = Literal["observed", "inferred", "uncertain"]


class EvidenceReference(BaseModel):
    file_id: str
    filename: str
    chunk_index: int
    score: float | None = None


class ClassifiedFinding(BaseModel):
    statement: str
    classification: ObservationClass
    evidence: list[EvidenceReference] = Field(default_factory=list)


class IndustrialAnalysis(BaseModel):
    analysis_type: Literal["process", "safety", "equipment", "procedure", "comparison"]
    findings: list[ClassifiedFinding] = Field(default_factory=list)
    evidence: list[EvidenceReference] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    disclaimer: str | None = None


class IndustrialReport(BaseModel):
    title: str
    objective: str
    findings: list[ClassifiedFinding] = Field(default_factory=list)
    calculations: list[dict] = Field(default_factory=list)
    evidence: list[EvidenceReference] = Field(default_factory=list)
    observations: list[str] = Field(default_factory=list)
    risks_warnings: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    conclusion: str
    generated_at: datetime
    request_id: str
