import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

from src.app import run_app
from src.settings import load_settings, ensure_directories


if __name__ == "__main__":
    settings = load_settings()
    ensure_directories(settings)
    run_app(settings)
