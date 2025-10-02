"""Configuration helpers for different environments."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class Config:
    debug: bool = False
    testing: bool = False
    firestore_project_id: str | None = None
    firestore_emulator_host: str | None = None
    secret_key: str | None = None


def load_config(env: str | None = None) -> Dict[str, Any]:
    """Return a mapping with configuration values based on the environment."""
    env_name = (env or os.environ.get("FLASK_ENV") or "development").lower()

    firestore_project_id = os.environ.get("FIRESTORE_PROJECT_ID")
    firestore_emulator_host = os.environ.get("FIRESTORE_EMULATOR_HOST")
    secret_key = os.environ.get("SECRET_KEY")

    match env_name:
        case "production":
            config = Config(
                firestore_project_id=firestore_project_id,
                firestore_emulator_host=firestore_emulator_host,
                secret_key=secret_key,
            )
        case "testing":
            config = Config(
                testing=True,
                firestore_project_id=firestore_project_id,
                firestore_emulator_host=firestore_emulator_host,
                secret_key=secret_key,
            )
        case _:
            config = Config(
                debug=True,
                firestore_project_id=firestore_project_id,
                firestore_emulator_host=firestore_emulator_host or "localhost:8080",
                secret_key=secret_key or "dev-secret-key",
            )

    return {
        "DEBUG": config.debug,
        "TESTING": config.testing,
        "FIRESTORE_PROJECT_ID": config.firestore_project_id,
        "FIRESTORE_EMULATOR_HOST": config.firestore_emulator_host,
        "SECRET_KEY": config.secret_key,
    }
