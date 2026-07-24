from app.domain.models import AuditEvent
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditEvent]):
    collection = "audit"
    model = AuditEvent

    def list_for_workspace(self, workspace_id: str | None = None) -> list[AuditEvent]:
        if workspace_id is None:
            return self.list()
        return self.list(filters={"workspace_id": workspace_id})
