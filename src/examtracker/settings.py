from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml  # type: ignore
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Used for searching the config
APP_NAME = "examtracker"


def get_default_data_dir() -> Path:
    base_dir = Path(__file__).resolve().parent.parent.parent  # project root
    return base_dir / "data"


def yaml_config_settings_source(settings_cls) -> Dict[str, Any]:
    config_path = os.getenv("EXAMTRACKER_CONFIG")

    if config_path:
        path = Path(config_path).expanduser()
        if path.exists():
            with open(path, "r") as f:
                return yaml.safe_load(f) or {}

    user_config = Path.home() / ".config" / APP_NAME / "config.yml"

    if user_config.exists():
        with open(user_config, "r") as f:
            return yaml.safe_load(f) or {}

    return {}


class Settings(BaseSettings):
    database_path: str = Field(default=str(get_default_data_dir() / "test.db"))
    css_path: str = Field(default=str(get_default_data_dir() / "style.css"))

    model_config = SettingsConfigDict(
        env_prefix="EXAMTRACKER_",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            env_settings,
            lambda: yaml_config_settings_source(settings_cls),
            dotenv_settings,
            file_secret_settings,
        )


def main() -> int:
    res = get_default_data_dir()
    print(res)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
