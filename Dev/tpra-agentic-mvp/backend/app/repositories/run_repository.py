from app.domain.models import Run
from app.repositories.base import BaseRepository


class RunRepository(BaseRepository[Run]):
    collection = "runs"
    model = Run

    def list_for_workspace(self, workspace_id: str) -> list[Run]:
        return self.list(filters={"workspace_id": workspace_id})
