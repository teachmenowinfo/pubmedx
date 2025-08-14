from pathlib import Path

from app.core.config import STATIC_DIR, TEMPLATES_DIR


def get_templates_dir() -> Path:
    return TEMPLATES_DIR


def get_static_dir() -> Path:
    return STATIC_DIR


