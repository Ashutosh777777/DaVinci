from datetime import datetime
from pydantic import BaseModel, Field


class BlogRequest(BaseModel):
    topic: str = Field(..., min_length=3)
    weekly_notes: str = Field(default="")
    scheduled_for: datetime | None = None
    target_audience: str = "developers and tech readers"
    tone: str = "clear, practical and engaging"
    devto_tags: list[str] = Field(default_factory=lambda: ["ai", "programming", "productivity"])
    publish_to_devto: bool = False
    generate_images: bool = True


class BlogResult(BaseModel):
    job_id: str
    status: str
    title: str | None = None
    markdown_path: str | None = None
    cover_image_path: str | None = None
    devto_url: str | None = None
    error: str | None = None
