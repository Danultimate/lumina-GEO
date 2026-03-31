from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str
    firecrawl_api_key: str
    gemini_model: str = "gemini-1.5-pro"
    output_dir: str = "."

    class Config:
        env_file = ".env"


settings = Settings()
