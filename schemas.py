from typing import Any
from pydantic import BaseModel, Field

class RecipientInput(BaseModel):
    # Optional fields let the API report one recipient's invalid data without
    # rejecting the entire bulk request.
    name: Any = None
    email: Any = None

class CreateJobRequest(BaseModel):
    event_name: str = Field(min_length=1, max_length=200)
    issuer: str = Field(min_length=1, max_length=200)
    certificate_date: str = Field(min_length=1, max_length=40)
    recipients: list[RecipientInput] = Field(min_length=1, max_length=1000)
