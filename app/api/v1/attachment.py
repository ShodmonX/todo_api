from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse

from pathlib import Path
from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.api.v1.deps import check_task_access, ensure_attachment_access
from app.schemas import AttachmentOut, MimeTypeEnum
from app.crud import (
    delete_attachment,
)
from app.models import User, Attachment
from app.config import settings
from app.utils.storage import build_storage_paths, save_upload_file


router = APIRouter(
    prefix="/attachments",
    tags=["Attachments"],
)

MEDIA_ROOT = Path(settings.MEDIA_ROOT)


@router.get("/{attachment_id}", response_model=AttachmentOut)
async def get_attachment_info(
    attachment: Annotated[Attachment, Depends(ensure_attachment_access)],
):
    return attachment


@router.delete("/{attachment_id}")
async def delete_attachment_by_id(
    attachment: Annotated[Attachment, Depends(ensure_attachment_access)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    resolved_media_root = MEDIA_ROOT.resolve()
    file_path = (MEDIA_ROOT / attachment.file_path).resolve()
    try:
        file_path.relative_to(resolved_media_root)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attachment path")

    await delete_attachment(session, attachment.id)

    if file_path.exists():
        file_path.unlink()

    return {"status": "ok", "message": "Attachment deleted"}


@router.get("/{attachment_id}/download")
async def download_attachment(
    attachment: Annotated[Attachment, Depends(ensure_attachment_access)],
):
    resolved_media_root = MEDIA_ROOT.resolve()
    file_path = (MEDIA_ROOT / attachment.file_path).resolve()
    try:
        file_path.relative_to(resolved_media_root)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attachment path")

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type=attachment.mime_type.value,
        filename=attachment.filename,
    )


@router.post("/bulk", response_model=list[AttachmentOut], status_code=201)
async def bulk_upload_attachments(
    task_id: Annotated[int, Form(...)],
    files: Annotated[list[UploadFile], File(...)],
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    task = await check_task_access(task_id, user, session)

    allowed_types = [mime.value for mime in MimeTypeEnum]
    MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

    saved_files: list[Path] = []
    attachments: list[Attachment] = []

    try:
        for upload in files:
            if not upload.content_type or upload.content_type not in allowed_types:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {upload.filename}")

            abs_path, rel_path = build_storage_paths(task.id, upload.filename or "uploaded_file", MEDIA_ROOT)
            written_size = await save_upload_file(upload, abs_path)
            saved_files.append(abs_path)

            attachment = Attachment(
                filename=upload.filename or "uploaded_file",
                file_path=rel_path,
                file_size=written_size,
                mime_type=MimeTypeEnum(upload.content_type),
                task_id=task.id,
                user_id=user.id,
            )
            attachments.append(attachment)
            session.add(attachment)

        await session.commit()
        for att in attachments:
            await session.refresh(att)

        return attachments
    except HTTPException:
        await session.rollback()
        for path in saved_files:
            if path.exists():
                path.unlink()
        raise
    except Exception as exc:  # pragma: no cover - defensive
        await session.rollback()
        for path in saved_files:
            if path.exists():
                path.unlink()
        raise HTTPException(status_code=500, detail=str(exc))
