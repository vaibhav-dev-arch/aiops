from app.domain.models import FileRecord
from app.repositories.base import BaseRepository


class FileRepository(BaseRepository[FileRecord]):
    collection = "files"
    model = FileRecord

    def list_for_workspace(self, workspace_id: str) -> list[FileRecord]:
        return self.list(filters={"workspace_id": workspace_id})
