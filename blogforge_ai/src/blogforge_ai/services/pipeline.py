import os
import traceback
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from blogforge_ai.config import settings
from blogforge_ai.crew import BlogForgeCrew
from blogforge_ai.schemas import BlogRequest, BlogResult
from blogforge_ai.tools.devto_tool import DevToPostTool
from blogforge_ai.tools.hf_image_tool import HuggingFaceImageTool
from blogforge_ai.utils import extract_title, parse_image_prompts, slugify, write_text

load_dotenv()


def _task_raw(output: Any, index: int) -> str:
    try:
        task_output = output.tasks_output[index]
        return getattr(task_output, "raw", None) or str(task_output)
    except Exception:
        return str(output)


def _public_image_url(local_path: str | None) -> str | None:
    if not local_path or not settings.image_public_base_url:
        return None
    return settings.image_public_base_url.rstrip("/") + "/" + Path(local_path).name


def run_blog_pipeline(request: BlogRequest, job_id: str | None = None) -> BlogResult:
    job_id = job_id or str(uuid.uuid4())
    try:
        missing = [name for name in ["GROQ_API_KEY", "SERPER_API_KEY"] if not os.getenv(name)]
        if missing:
            raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

        crew = BlogForgeCrew(verbose=True)
        output = crew.kickoff(
            inputs={
                "topic": request.topic,
                "weekly_notes": request.weekly_notes or "No weekly notes provided. Use the selected topic as the anchor.",
                "target_audience": request.target_audience,
                "tone": request.tone,
            }
        )

        final_markdown = _task_raw(output, -2)
        image_prompt_text = _task_raw(output, -1)
        title = extract_title(final_markdown, request.topic)
        slug = slugify(title)

        dated_dir = settings.output_path / datetime.now().strftime("%Y-%m-%d") / f"{slug}-{job_id[:8]}"
        markdown_path = write_text(dated_dir / "blog.md", final_markdown)
        write_text(dated_dir / "image_prompts.txt", image_prompt_text)

        cover_image_path = None
        cover_prompt, _inline_prompt = parse_image_prompts(image_prompt_text)
        if request.generate_images and cover_prompt:
            image_tool = HuggingFaceImageTool()
            image_result = image_tool._run(cover_prompt, filename_prefix=f"cover-{slug}")
            if image_result.endswith(".png"):
                cover_image_path = image_result

        devto_url = None
        if request.publish_to_devto:
            devto_tool = DevToPostTool()
            post_result = devto_tool._run(
                title=title,
                markdown=final_markdown,
                tags=request.devto_tags,
                cover_image=_public_image_url(cover_image_path),
                publish=settings.devto_publish,
            )
            if post_result.startswith("http"):
                devto_url = post_result
            else:
                write_text(dated_dir / "devto_post_result.txt", post_result)

        return BlogResult(
            job_id=job_id,
            status="completed",
            title=title,
            markdown_path=markdown_path,
            cover_image_path=cover_image_path,
            devto_url=devto_url,
        )
    except Exception as exc:
        error_path = settings.output_path / f"error-{job_id}.log"
        write_text(error_path, traceback.format_exc())
        return BlogResult(job_id=job_id, status="failed", error=str(exc))
