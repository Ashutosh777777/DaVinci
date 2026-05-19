from typing import Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from blogforge_ai.config import settings


class DevToPostInput(BaseModel):
    title: str = Field(..., description="Article title")
    markdown: str = Field(..., description="Markdown body")
    tags: list[str] = Field(default_factory=list, description="DEV.to tags, max 4 recommended")
    cover_image: str | None = Field(default=None, description="Public cover image URL")
    publish: bool = Field(default=False, description="Whether to publish immediately")


class DevToPostTool(BaseTool):
    name: str = "Post article to DEV.to"
    description: str = "Creates a DEV.to article draft or published post using the DEV.to API. Requires DEVTO_API_KEY."
    args_schema: Type[BaseModel] = DevToPostInput

    def _run(self, title: str, markdown: str, tags: list[str] | None = None, cover_image: str | None = None, publish: bool = False) -> str:
        if not settings.devto_api_key:
            return "DEVTO_API_KEY is missing. DEV.to posting skipped."

        payload: dict = {
            "article": {
                "title": title,
                "body_markdown": markdown,
                "published": bool(publish),
                "tags": (tags or [])[:4],
            }
        }
        if cover_image:
            payload["article"]["main_image"] = cover_image
        if settings.devto_organization_id:
            payload["article"]["organization_id"] = int(settings.devto_organization_id)

        response = requests.post(
            "https://dev.to/api/articles",
            headers={"api-key": settings.devto_api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=60,
        )
        if response.status_code >= 400:
            return f"DEV.to post failed: {response.status_code} {response.text[:500]}"
        data = response.json()
        return data.get("url") or data.get("canonical_url") or str(data)
