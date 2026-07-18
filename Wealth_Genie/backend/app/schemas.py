from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional

class ErrorResponse(BaseModel):
    error: str
    detail: str
    status_code: int



class TokenVerificationResponse(BaseModel):
    user_id: UUID
    email: str
    aud: str
    role: str

class UploadResponse(BaseModel):
    document_id: UUID
    status: str

