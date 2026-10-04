from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str = "mock"  # mock | openai
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"

    prompt_version: str = "v2"

    db_path: str = "data/runs.db"
    golden_dataset_path: str = "data/golden_dataset.json"

    regression_tolerance: float = 0.02  # 2 percentage points

    slack_webhook_url: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
