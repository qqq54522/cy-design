from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8100
    debug: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def workspace_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent.parent

    @property
    def logs_dir(self) -> Path:
        return self.workspace_dir / "logs"


settings = Settings()
