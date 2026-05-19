import argparse
from datetime import datetime

from dotenv import load_dotenv

from blogforge_ai.schemas import BlogRequest
from blogforge_ai.services.pipeline import run_blog_pipeline


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Run BlogForge AI from the terminal")
    parser.add_argument("--topic", required=True)
    parser.add_argument("--notes", default="")
    parser.add_argument("--audience", default="developers and tech readers")
    parser.add_argument("--tone", default="clear, practical and engaging")
    parser.add_argument("--tags", default="ai,programming,productivity")
    parser.add_argument("--publish-to-devto", action="store_true")
    parser.add_argument("--no-images", action="store_true")
    args = parser.parse_args()

    request = BlogRequest(
        topic=args.topic,
        weekly_notes=args.notes,
        target_audience=args.audience,
        tone=args.tone,
        devto_tags=[t.strip() for t in args.tags.split(",") if t.strip()],
        publish_to_devto=args.publish_to_devto,
        generate_images=not args.no_images,
    )
    result = run_blog_pipeline(request)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
