"""Shared pytest fixtures."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import reset_settings_cache
from app.providers.registry import reset_registry


@pytest.fixture()
def tmp_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    data = tmp_path / "data"
    data.mkdir()
    monkeypatch.setenv("TPRA_DATA_DIR", str(data))
    monkeypatch.setenv("STORAGE_PROVIDER", "local")
    monkeypatch.setenv("METADATA_PROVIDER", "sqlite")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("AUTH_PROVIDER", "dev")
    monkeypatch.setenv("DOC_INTEL_PROVIDER", "local")
    monkeypatch.setenv("TPRA_ENV", "local")
    # Point config at project backend config
    backend_dir = Path(__file__).resolve().parents[1]
    monkeypatch.setenv("TPRA_CONFIG_PATH", str(backend_dir / "config.yaml"))
    # Override local paths via env after settings load — also set in config via data dir
    reset_settings_cache()
    reset_registry()
    yield data
    reset_settings_cache()
    reset_registry()


@pytest.fixture()
def client(tmp_data_dir: Path) -> TestClient:
    # Import after env is set so settings resolve correctly
    from app.core.config import get_settings
    from app.main import create_app

    settings = get_settings()
    # Force sqlite/storage under tmp
    settings.local.sqlite_path = str(tmp_data_dir / "tpra.db")
    settings.local.storage_root = str(tmp_data_dir / "files")
    reset_registry()

    app = create_app()
    with TestClient(app) as c:
        c.headers.update(
            {
                "x-user-id": "tester",
                "x-user-name": "Test User",
                "x-user-role": "admin",
            }
        )
        yield c


@pytest.fixture()
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"
