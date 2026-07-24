from app.domain.models import ReviewerDecision
from app.repositories.base import BaseRepository


class ReviewerLogRepository(BaseRepository[ReviewerDecision]):
    collection = "reviewer_log"
    model = ReviewerDecision

    def list_for_workspace(self, workspace_id: str) -> list[ReviewerDecision]:
        return self.list(filters={"workspace_id": workspace_id})
