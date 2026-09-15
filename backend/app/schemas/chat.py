from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: str | None = None
    file_id: str | None = None
    image_ref: str | None = None
    mode: str | None = None


class ChatResponse(BaseModel):
    request_id: str
    response: str
    answer: str = ""
    title: str | None = None
    task_type: str | None = None
    requires_file: bool | None = None
    file_type: str | None = None
    slide_count: int | None = None
    requested_format: str | None = None
    requested_sheets: list[str] | None = None
    outline: list[str] | None = None
    sources: list[dict] = []
    uncertainties: list[str] = []
    files: list[dict] = []
    comparison: list[dict] = []
    tool: str | None = None
    tool_result: dict | None = None
    industrial_analysis: dict | None = None
    status: str
