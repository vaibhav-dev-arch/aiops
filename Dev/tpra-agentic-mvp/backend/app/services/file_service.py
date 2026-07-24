"""File upload/download service."""

from __future__ import annotations

from app.core.exceptions import NotFoundError, ValidationError
from app.domain.models import AuditEvent, FileRecord, UserContext
from app.providers.base import StorageProvider
from app.repositories.audit_repository import AuditRepository
from app.repositories.file_repository import FileRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.services.authz import require_permission

MAX_UPLOAD_BYTES = 25 * 1024 * 1024


class FileService:
    def __init__(
        self,
        files: FileRepository,
        workspaces: WorkspaceRepository,
        storage: StorageProvider,
        audit: AuditRepository,
    ):
        self.files = files
        self.workspaces = workspaces
        self.storage = storage
        self.audit = audit

    def upload(
        self,
        *,
        workspace_id: str,
        filename: str,
        data: bytes,
        content_type: str,
        user: UserContext,
        tags: list[str] | None = None,
    ) -> FileRecord:
        require_permission(user, "file:upload")
        if not self.workspaces.get(workspace_id):
            raise NotFoundError(f"Workspace not found: {workspace_id}")
        if not filename:
            raise ValidationError("filename is required")
        if len(data) > MAX_UPLOAD_BYTES:
            raise ValidationError("File exceeds 25MB limit")

        record = FileRecord(
            workspace_id=workspace_id,
            filename=filename,
            content_type=content_type or "application/octet-stream",
            size=len(data),
            storage_key="",  # set below
            uploaded_by=user.user_id,
            tags=tags or [],
        )
        record.storage_key = f"{workspace_id}/{record.id}/{filename}"
        self.storage.put_bytes(record.storage_key, data, content_type=record.content_type)
        self.files.save(record)
        self.audit.save(
            AuditEvent(
                workspace_id=workspace_id,
                actor=user.user_id,
                action="file.upload",
                resource_type="file",
                resource_id=record.id,
                details={"filename": filename, "size": record.size},
            )
        )
        return record

    def list(self, workspace_id: str, user: UserContext) -> list[FileRecord]:
        require_permission(user, "file:download")
        if not self.workspaces.get(workspace_id):
            raise NotFoundError(f"Workspace not found: {workspace_id}")
        return self.files.list_for_workspace(workspace_id)

    def get(self, file_id: str, user: UserContext) -> FileRecord:
        require_permission(user, "file:download")
        record = self.files.get(file_id)
        if not record:
            raise NotFoundError(f"File not found: {file_id}")
        return record

    def download(self, file_id: str, user: UserContext) -> tuple[FileRecord, bytes]:
        record = self.get(file_id, user)
        data = self.storage.get_bytes(record.storage_key)
        return record, data
