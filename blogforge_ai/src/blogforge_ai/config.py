from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    serper_api_key: str | None = Field(default=None, alias="SERPER_API_KEY")
    hf_token: str | None = Field(default=None, alias="HF_TOKEN")
    devto_api_key: str | None = Field(default=None, alias="DEVTO_API_KEY")

    planner_model: str = Field(default="groq/llama-3.3-70b-versatile", alias="PLANNER_MODEL")
    writer_model: str = Field(default="groq/openai/gpt-oss-20b", alias="WRITER_MODEL")
    editor_model: str = Field(default="groq/openai/gpt-oss-20b", alias="EDITOR_MODEL")
    hf_image_model: str = Field(default="stabilityai/stable-diffusion-xl-base-1.0", alias="HF_IMAGE_MODEL")

    image_public_base_url: str | None = Field(default=None, alias="IMAGE_PUBLIC_BASE_URL")
    devto_publish: bool = Field(default=False, alias="DEVTO_PUBLISH")
    devto_organization_id: str | None = Field(default=None, alias="DEVTO_ORGANIZATION_ID")

    app_host: str = Field(default="127.0.0.1", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    database_path: str = Field(default="blogforge.sqlite3", alias="DATABASE_PATH")
    output_dir: str = Field(default="outputs", alias="OUTPUT_DIR")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def output_path(self) -> Path:
        path = Path(self.output_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


settings = Settings()
