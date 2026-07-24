"""Configuration loader: env > config.yaml > defaults."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class ProviderSettings(BaseModel):
    storage: str = "local"
    metadata: str = "sqlite"
    llm: str = "mock"
    auth: str = "dev"
    document_intelligence: str = "local"


class LocalSettings(BaseModel):
    storage_root: str = ".data/files"
    sqlite_path: str = ".data/tpra.db"


class AzureSettings(BaseModel):
    storage_connection_string: str = ""
    cosmos_endpoint: str = ""
    cosmos_key: str = ""
    cosmos_database: str = "tpra"
    openai_endpoint: str = ""
    openai_api_key: str = ""
    openai_deployment: str = "gpt-4o"
    doc_intel_endpoint: str = ""
    doc_intel_key: str = ""


class ObservabilitySettings(BaseModel):
    log_level: str = "INFO"
    json_logs: bool = True


class Settings(BaseModel):
    environment: str = "local"
    data_dir: str = ".data"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    providers: ProviderSettings = Field(default_factory=ProviderSettings)
    local: LocalSettings = Field(default_factory=LocalSettings)
    azure: AzureSettings = Field(default_factory=AzureSettings)
    observability: ObservabilitySettings = Field(default_factory=ObservabilitySettings)
    project_root: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[3])
    foundry_agents_path: Path | None = None
    prompts_root: Path | None = None

    def resolve_paths(self) -> "Settings":
        root = self.project_root
        data = Path(self.data_dir)
        if not data.is_absolute():
            data = (root / data).resolve()
        else:
            data = data.resolve()
        self.data_dir = str(data)
        # Prefer data_dir children when using defaults or relative paths
        storage = Path(self.local.storage_root)
        if not storage.is_absolute():
            self.local.storage_root = str((data / "files").resolve())
        sqlite = Path(self.local.sqlite_path)
        if not sqlite.is_absolute():
            self.local.sqlite_path = str((data / "tpra.db").resolve())
        self.foundry_agents_path = root / "foundry" / "agents.yaml"
        self.prompts_root = root / "prompts"
        return self


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data if isinstance(data, dict) else {}


def _env_overrides() -> dict[str, Any]:
    providers: dict[str, Any] = {}
    mapping = {
        "STORAGE_PROVIDER": "storage",
        "METADATA_PROVIDER": "metadata",
        "LLM_PROVIDER": "llm",
        "AUTH_PROVIDER": "auth",
        "DOC_INTEL_PROVIDER": "document_intelligence",
    }
    for env_key, cfg_key in mapping.items():
        if env_key in os.environ:
            providers[cfg_key] = os.environ[env_key]

    overrides: dict[str, Any] = {}
    if "TPRA_ENV" in os.environ:
        overrides["environment"] = os.environ["TPRA_ENV"]
    if "TPRA_DATA_DIR" in os.environ:
        overrides["data_dir"] = os.environ["TPRA_DATA_DIR"]
    if "TPRA_CORS_ORIGINS" in os.environ:
        overrides["cors_origins"] = [
            o.strip() for o in os.environ["TPRA_CORS_ORIGINS"].split(",") if o.strip()
        ]
    if providers:
        overrides["providers"] = providers

    azure: dict[str, Any] = {}
    azure_map = {
        "AZURE_STORAGE_CONNECTION_STRING": "storage_connection_string",
        "AZURE_COSMOS_ENDPOINT": "cosmos_endpoint",
        "AZURE_COSMOS_KEY": "cosmos_key",
        "AZURE_OPENAI_ENDPOINT": "openai_endpoint",
        "AZURE_OPENAI_API_KEY": "openai_api_key",
        "AZURE_OPENAI_DEPLOYMENT": "openai_deployment",
        "AZURE_DOC_INTEL_ENDPOINT": "doc_intel_endpoint",
        "AZURE_DOC_INTEL_KEY": "doc_intel_key",
    }
    for env_key, cfg_key in azure_map.items():
        if env_key in os.environ:
            azure[cfg_key] = os.environ[env_key]
    if azure:
        overrides["azure"] = azure
    return overrides


@lru_cache
def get_settings() -> Settings:
    backend_dir = Path(__file__).resolve().parents[2]
    project_root = backend_dir.parent
    config_path = Path(os.environ.get("TPRA_CONFIG_PATH", str(backend_dir / "config.yaml")))
    if not config_path.is_absolute():
        # Prefer CWD-relative, then project root
        candidates = [Path.cwd() / config_path, project_root / config_path, backend_dir / config_path.name]
        config_path = next((c for c in candidates if c.exists()), candidates[0])

    raw = _load_yaml(config_path)
    raw = _deep_merge(raw, _env_overrides())
    raw["project_root"] = project_root
    settings = Settings.model_validate(raw)
    return settings.resolve_paths()


def reset_settings_cache() -> None:
    get_settings.cache_clear()
