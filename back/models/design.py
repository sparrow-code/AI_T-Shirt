from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DesignRequest(BaseModel):
    prompt: str
    style: Optional[str] = "realistic"
    colors: Optional[List[str]] = []
    size: Optional[str] = "M"
    priority: Optional[int] = Field(1, ge=1, le=5)
    callback_url: Optional[str] = None