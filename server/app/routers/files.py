from pathlib import Path

from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/files/{job_id}/{filename}")
def get_file(
    job_id: str,
    filename: str,
):
    file_path = Path("workspaces") / job_id / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream",
    )
