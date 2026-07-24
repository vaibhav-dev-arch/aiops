"""Provider registry / DI factory."""

from __future__ import annotations

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.providers.auth.client_sso import ClientSSOAuthProvider
from app.providers.auth.dev import DevAuthProvider
from app.providers.base import (
    AuthProvider,
    DocIntelligenceProvider,
    LLMProvider,
    MetadataProvider,
    StorageProvider,
)
from app.providers.document_intelligence.azure import AzureDocIntelligenceProvider
from app.providers.document_intelligence.local import LocalDocIntelligenceProvider
from app.providers.llm.azure_openai import AzureOpenAILLMProvider
from app.providers.llm.foundry import FoundryLLMProvider
from app.providers.llm.mock import MockLLMProvider
from app.providers.metadata.cosmos import CosmosMetadataProvider
from app.providers.metadata.sqlite import SqliteMetadataProvider
from app.providers.storage.azure_blob import AzureBlobStorageProvider
from app.providers.storage.local import LocalStorageProvider


class ProviderRegistry:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._storage: StorageProvider | None = None
        self._metadata: MetadataProvider | None = None
        self._llm: LLMProvider | None = None
        self._auth: AuthProvider | None = None
        self._doc_intel: DocIntelligenceProvider | None = None

    @property
    def storage(self) -> StorageProvider:
        if self._storage is None:
            kind = self.settings.providers.storage
            if kind == "azure":
                self._storage = AzureBlobStorageProvider(
                    self.settings.azure.storage_connection_string
                )
            else:
                self._storage = LocalStorageProvider(self.settings.local.storage_root)
        return self._storage

    @property
    def metadata(self) -> MetadataProvider:
        if self._metadata is None:
            kind = self.settings.providers.metadata
            if kind == "cosmos":
                self._metadata = CosmosMetadataProvider(
                    self.settings.azure.cosmos_endpoint,
                    self.settings.azure.cosmos_key,
                    self.settings.azure.cosmos_database,
                )
            else:
                self._metadata = SqliteMetadataProvider(self.settings.local.sqlite_path)
        return self._metadata

    @property
    def llm(self) -> LLMProvider:
        if self._llm is None:
            kind = self.settings.providers.llm
            if kind == "azure_openai":
                self._llm = AzureOpenAILLMProvider(
                    self.settings.azure.openai_endpoint,
                    self.settings.azure.openai_api_key,
                    self.settings.azure.openai_deployment,
                )
            elif kind == "foundry":
                self._llm = FoundryLLMProvider()
            else:
                self._llm = MockLLMProvider()
        return self._llm

    @property
    def auth(self) -> AuthProvider:
        if self._auth is None:
            kind = self.settings.providers.auth
            if kind == "client_sso":
                self._auth = ClientSSOAuthProvider()
            else:
                self._auth = DevAuthProvider()
        return self._auth

    @property
    def document_intelligence(self) -> DocIntelligenceProvider:
        if self._doc_intel is None:
            kind = self.settings.providers.document_intelligence
            if kind == "azure":
                self._doc_intel = AzureDocIntelligenceProvider(
                    self.settings.azure.doc_intel_endpoint,
                    self.settings.azure.doc_intel_key,
                )
            else:
                self._doc_intel = LocalDocIntelligenceProvider()
        return self._doc_intel

    def provider_map(self) -> dict[str, str]:
        return {
            "storage": self.settings.providers.storage,
            "metadata": self.settings.providers.metadata,
            "llm": self.settings.providers.llm,
            "auth": self.settings.providers.auth,
            "document_intelligence": self.settings.providers.document_intelligence,
        }


@lru_cache
def get_registry() -> ProviderRegistry:
    return ProviderRegistry(get_settings())


def reset_registry() -> None:
    get_registry.cache_clear()
