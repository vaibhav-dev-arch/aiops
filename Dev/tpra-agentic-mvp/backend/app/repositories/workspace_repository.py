from app.domain.models import Workspace
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    collection = "workspaces"
    model = Workspace
