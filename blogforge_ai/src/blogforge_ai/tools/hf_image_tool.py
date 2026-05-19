import base64
import re
import time
from pathlib import Path
from typing import Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from blogforge_ai.config import settings


class HuggingFaceImageInput(BaseModel):
    prompt: str = Field(..., description="Image prompt. Ask for no text inside the image.")
    filename_prefix: str = Field(default="blog-image", description="Safe filename prefix")


class HuggingFaceImageTool(BaseTool):
    name: str = "Generate blog image with Hugging Face"
    description: str = "Generates a blog image using the Hugging Face Inference API and saves it locally. Returns the saved file path."
    args_schema: Type[BaseModel] = HuggingFaceImageInput

    def _run(self, prompt: str, filename_prefix: str = "blog-image") -> str:
        if not settings.hf_token:
            return "HF_TOKEN is missing. Image generation skipped."

        safe_prefix = re.sub(r"[^a-zA-Z0-9_-]+", "-", filename_prefix).strip("-") or "blog-image"
        out_dir = settings.output_path / "images"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{safe_prefix}-{int(time.time())}.png"

        url = f"https://api-inference.huggingface.co/models/{settings.hf_image_model}"
        headers = {"Authorization": f"Bearer {settings.hf_token}"}
        payload = {"inputs": prompt, "parameters": {"num_inference_steps": 30}}
        response = requests.post(url, headers=headers, json=payload, timeout=180)

        if response.status_code >= 400:
            return f"Hugging Face image generation failed: {response.status_code} {response.text[:500]}"

        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            data = response.json()
            if isinstance(data, dict) and "image" in data:
                out_file.write_bytes(base64.b64decode(data["image"]))
            else:
                return f"Unexpected Hugging Face JSON response: {data}"
        else:
            out_file.write_bytes(response.content)

        return str(out_file)
