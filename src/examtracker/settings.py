from __future__ import annotations

import os
import sys
from importlib.resources import files
from pathlib import Path
from typing import Any, Dict

import yaml  # type: ignore
from platformdirs import PlatformDirs
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_NAME = "examtracker"
APP_AUTHOR = "Samuel Huwiler"

dirs = PlatformDirs(appname=APP_NAME, appauthor=APP_AUTHOR)


def get_config_dir() -> Path:
    if sys.platform == "darwin":
        # Force ~/.config instead of ~/Library/Application Support
        return Path.home() / ".config" / APP_NAME
    else:
        # Linux & Windows default
        return Path(dirs.user_config_dir)


def get_default_database_uri() -> str:
    """Return a writable database path in the user data directory."""

    db_dir = get_config_dir()
    db_dir.mkdir(parents=True, exist_ok=True)
    return "sqlite:///" + str(db_dir / "examtracker.db")


def get_default_css_path() -> Path:
    """Return the path to the CSS inside the package data folder."""
    return Path(files("examtracker").joinpath("data/style.css"))  # type:ignore


def yaml_config_settings_source(settings_cls) -> Dict[str, Any]:
    config_path = os.getenv("EXAMTRACKER_CONFIG")

    if config_path:
        path = Path(config_path).expanduser()
        if path.exists():
            with open(path, "r") as f:
                return yaml.safe_load(f) or {}

    user_config = get_config_dir() / "config.yml"

    if user_config.exists():
        with open(user_config, "r") as f:
            return yaml.safe_load(f) or {}

    return {}


class Settings(BaseSettings):
    database_uri: str = Field(default_factory=lambda: str(get_default_database_uri()))
    css_path: str = Field(default_factory=lambda: str(get_default_css_path()))
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
    print(Settings())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
