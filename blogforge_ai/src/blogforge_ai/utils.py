import re
from pathlib import Path


def slugify(text: str, max_len: int = 80) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return (text[:max_len].strip("-") or "blog")


def extract_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback.strip() or "Untitled Blog"


def write_text(path: Path, text: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)


def parse_image_prompts(text: str) -> tuple[str | None, str | None]:
    cover = None
    inline = None
    for line in text.splitlines():
        if line.upper().startswith("COVER_PROMPT:"):
            cover = line.split(":", 1)[1].strip()
        if line.upper().startswith("INLINE_PROMPT:"):
            inline = line.split(":", 1)[1].strip()
    return cover, inline
