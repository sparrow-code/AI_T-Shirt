from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

# Enum for style field
class Style(str, Enum):
    realistic = "realistic"
    abstract = "abstract"
    cartoon = "cartoon"
    flat = "flat"

# Request Schema
class ImageGenerateRequest(BaseModel):
    prompt: str = Field(..., example="Drone Logo, professional product photography, centered composition, high quality")
    style: Style = Field(..., example="realistic", description="Style of the image")
    colors: List[str] = Field(default=[], example=["red", "blue"], description="List of colors to include")
    size: str = Field(..., example="M", description="Size of the output image (S, M, L, etc.)")
    priority: Optional[int] = Field(default=1, example=1, description="Priority level of the request")

class BGRemoveRequest(BaseModel) :
    image_url: str = Field(..., example="/image/username/image.png", description="URL of the image to process")
    model: str = Field("u2net", example="u2net", description="The model to use for image processing")
    return_mask: bool = Field(False, example=False, description="Whether to return the mask")
    transparency: float = Field(0.0, ge=0.0, le=1.0, example=0.0, description="Transparency level (0.0 to 1.0)")
