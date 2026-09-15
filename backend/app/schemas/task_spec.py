from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class TaskSpec:
    request_id: str
    workspace_id: str
    mode: str  # "generate_ppt" | "generate_excel" | "generate_report" | "chat"
    user_query: str
    title: str
    audience: str | None
    deliverable_type: str  # "pptx" | "xlsx" | "docx" | "answer"
    slide_count: int = 6
    requested_sections: list[str] = field(default_factory=list)
    requested_sheets: list[str] = field(default_factory=list)
    requested_columns: list[str] = field(default_factory=list)
    requested_filters: list[str] = field(default_factory=list)
    requested_charts: list[str] = field(default_factory=list)
    requested_constraints: list[str] = field(default_factory=list)
    retrieval_queries: list[str] = field(default_factory=list)
    source_evidence: list[dict[str, Any]] = field(default_factory=list)
    output_filename: str = ""
