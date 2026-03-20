"""后端基础配置 - 各模块 Settings 可继承此基类，避免重复定义公共字段。"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings


class BaseBackendSettings(BaseSettings):
    """后端模块公共配置基类"""

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    DATA_DIR: Path = Path.cwd() / "data"
    DATA_RETENTION_DAYS: int = 30

    MAX_CONCURRENT: int = 3
    RATE_LIMIT_PER_MINUTE: int = 10
    MAX_RETRIES: int = 3
    RETRY_BASE_DELAY: float = 1.0

    LOG_LEVEL: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def projects_dir(self) -> Path:
        return self.DATA_DIR / "projects"

    @property
    def logs_dir(self) -> Path:
        return self.DATA_DIR / "logs"
