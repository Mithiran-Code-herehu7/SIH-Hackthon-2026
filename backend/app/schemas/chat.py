from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    session_id: str | None = None
    file_id: str | None = None
    image_ref: str | None = None


class ChatResponse(BaseModel):
    request_id: str
    response: str
    sources: list[dict] = []
    tool: str | None = None
    tool_result: dict | None = None
    industrial_analysis: dict | None = None
    status: str
