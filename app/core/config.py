from pathlib import Path


def get_app_dir() -> Path:
    return Path(__file__).resolve().parents[1]


APP_DIR: Path = get_app_dir()
PROJECT_ROOT: Path = APP_DIR.parent
TEMPLATES_DIR: Path = APP_DIR / "templates"
STATIC_DIR: Path = APP_DIR / "static"


