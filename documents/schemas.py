from datetime import datetime

from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    file_id: str
    filename: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime


class DocumentResponse(BaseModel):
    file_id: str
    filename: str
    content_type: str
    size_bytes: int
    uploaded_at: datetime
    status: str