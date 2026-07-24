from fastapi import APIRouter, Depends, File, Form, UploadFile
from fastapi.responses import Response

from app.api.deps import current_user, file_service
from app.domain.models import UserContext
from app.schemas.api import FileResponse
from app.services.file_service import FileService

router = APIRouter(tags=["files"])


@router.post("/workspaces/{workspace_id}/files", response_model=FileResponse, status_code=201)
async def upload_file(
    workspace_id: str,
    upload: UploadFile = File(...),
    tags: str = Form(""),
    service: FileService = Depends(file_service),
    user: UserContext = Depends(current_user),
) -> FileResponse:
    data = await upload.read()
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    record = service.upload(
        workspace_id=workspace_id,
        filename=upload.filename or "upload.bin",
        data=data,
        content_type=upload.content_type or "application/octet-stream",
        user=user,
        tags=tag_list,
    )
    return FileResponse.model_validate(record.model_dump(mode="json"))


@router.get("/workspaces/{workspace_id}/files", response_model=list[FileResponse])
def list_files(
    workspace_id: str,
    service: FileService = Depends(file_service),
    user: UserContext = Depends(current_user),
) -> list[FileResponse]:
    return [FileResponse.model_validate(f.model_dump(mode="json")) for f in service.list(workspace_id, user)]


@router.get("/files/{file_id}", response_model=FileResponse)
def get_file_meta(
    file_id: str,
    service: FileService = Depends(file_service),
    user: UserContext = Depends(current_user),
) -> FileResponse:
    return FileResponse.model_validate(service.get(file_id, user).model_dump(mode="json"))


@router.get("/files/{file_id}/download")
def download_file(
    file_id: str,
    service: FileService = Depends(file_service),
    user: UserContext = Depends(current_user),
) -> Response:
    record, data = service.download(file_id, user)
    return Response(
        content=data,
        media_type=record.content_type,
        headers={"Content-Disposition": f'attachment; filename="{record.filename}"'},
    )
