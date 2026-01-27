from pathlib import Path
from uuid import uuid4
from typing import Tuple

import aiofiles
from fastapi import UploadFile


def build_storage_paths(task_id: int, original_filename: str, media_root: Path) -> Tuple[Path, str]:
    """Create absolute and relative paths for storing an uploaded file."""
    media_root = Path(media_root)
    safe_name = Path(original_filename or "file").name
    ext = Path(safe_name).suffix
    generated_name = f"{uuid4().hex}{ext}"
    relative_path = Path(str(task_id)) / generated_name
    absolute_path = media_root / relative_path
    return absolute_path, relative_path.as_posix()


async def save_upload_file(upload: UploadFile, destination: Path, chunk_size: int = 1_048_576) -> int:
    """Stream an UploadFile to disk and return the number of bytes written."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    total_written = 0
    async with aiofiles.open(destination, "wb") as output_file:
        while True:
            chunk = await upload.read(chunk_size)
            if not chunk:
                break
            total_written += len(chunk)
            await output_file.write(chunk)

    await upload.seek(0)
    return total_written
