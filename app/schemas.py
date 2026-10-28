from typing import Literal
from pydantic import BaseModel, Field


class IncomingMessage(BaseModel):
    sender: str = Field(min_length=1, max_length=200)
    channel: Literal["email", "chat", "form"] = "email"
    text: str = Field(min_length=1, max_length=10_000)