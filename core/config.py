"""JARVIS configuration management."""

import os
from pathlib import Path
from typing import Any, Optional

import yaml
from dotenv import load_dotenv

from core.logger import get_logger
from core.exceptions import ConfigurationError

logger = get_logger("config")


class Config:
    """Centralized configuration manager."""

    _instance: Optional["Config"] = None
    _loaded: bool = False

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._loaded:
            return
        self._data: dict = {}
        self._project_root = Path(__file__).resolve().parent.parent
        self._load()
        self._loaded = True

    @property
    def project_root(self) -> Path:
        return self._project_root

    def _load(self) -> None:
        """Load configuration from .env and config.yaml."""
        # Load .env
        env_path = self._project_root / ".env"
        if env_path.exists():
            load_dotenv(str(env_path))
            logger.info("Loaded .env file.")
        else:
            logger.info("No .env file found; using defaults and environment variables.")

        # Load config.yaml
        config_path = self._project_root / "config" / "config.yaml"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    self._data = yaml.safe_load(f) or {}
                logger.info("Loaded config/config.yaml.")
            except Exception as e:
                logger.warning(f"Failed to load config.yaml: {e}")
                self._data = {}
        else:
            example_path = self._project_root / "config" / "config.example.yaml"
            if example_path.exists():
                try:
                    with open(example_path, "r", encoding="utf-8") as f:
                        self._data = yaml.safe_load(f) or {}
                    logger.info("Loaded config/config.example.yaml as fallback.")
                except Exception as e:
                    logger.warning(f"Failed to load config.example.yaml: {e}")
                    self._data = {}
            else:
                logger.warning("No configuration file found; using defaults.")
                self._data = {}

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get config value by dot-separated path. e.g. 'ai.ollama_model'."""
        keys = key_path.split(".")
        value = self._data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default
            if value is None:
                return default
        return value

    def env(self, key: str, default: str = "") -> str:
        """Get environment variable."""
        return os.environ.get(key, default)

    def env_int(self, key: str, default: int = 0) -> int:
        """Get environment variable as integer."""
        try:
            return int(os.environ.get(key, str(default)))
        except (ValueError, TypeError):
            return default

    def env_bool(self, key: str, default: bool = False) -> bool:
        """Get environment variable as boolean."""
        val = os.environ.get(key, "").lower()
        if val in ("1", "true", "yes", "on"):
            return True
        if val in ("0", "false", "no", "off"):
            return False
        return default

    @property
    def ollama_base_url(self) -> str:
        return self.env("OLLAMA_BASE_URL", self.get("ai.ollama_base_url", "http://localhost:11434"))

    @property
    def ollama_model(self) -> str:
        return self.env("OLLAMA_MODEL", self.get("ai.ollama_model", "llama3"))

    @property
    def haven_root(self) -> Optional[Path]:
        val = self.env("HAVEN_ROOT", self.get("haven.root", ""))
        if val:
            p = Path(val)
            if p.exists():
                return p
            logger.warning(f"HAVEN_ROOT path does not exist: {val}")
        return None

    @property
    def batch_size(self) -> int:
        return self.env_int("BATCH_SIZE", self.get("batch.default_size", 5))

    @property
    def stt_model(self) -> str:
        return self.env("STT_MODEL", self.get("voice.stt_model", "base"))

    @property
    def log_level(self) -> str:
        return self.env("LOG_LEVEL", self.get("logging.level", "INFO"))

    @property
    def data_dir(self) -> Path:
        d = self._project_root / "data"
        d.mkdir(parents=True, exist_ok=True)
        return d

    @property
    def database_path(self) -> Path:
        p = self.data_dir / "database" / "jarvis.db"
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def log_file(self) -> str:
        return self.get("logging.file", "data/logs/jarvis.log")

    def as_dict(self) -> dict:
        return dict(self._data)
