from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from sqlalchemy.orm import Session

from apps.api.database.session import get_db
from apps.api.models.audit import AuditEvent
from apps.api.models.enums import AuditEventType, JobStatus
from apps.api.models.print_job import PrintJob
from apps.api.models.user import User
from apps.api.schemas.job import JobOut
from apps.api.security.auth import get_current_active_user
from apps.api.services.engine_loader import audit_service
from apps.api.services.pipeline import run_analysis_pipeline
from apps.api.services.storage import UploadValidationError, save_upload

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/analyze", response_model=JobOut, status_code=202)
async def analyze_document(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    try:
        stored_path, display_filename, sha256_hex, _size = await save_upload(file)
    except UploadValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    job = PrintJob(
        user_id=user.id,
        original_filename=display_filename,
        sha256=sha256_hex,
        original_path=str(stored_path),
        status=JobStatus.UPLOADED,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    audit_service.record_event(
        db,
        AuditEvent,
        event_type=AuditEventType.JOB_RECEIVED.value,
        job_id=job.id,
        user_id=user.id,
        message=f"Received {display_filename}",
    )

    background_tasks.add_task(run_analysis_pipeline, job.id)
    return job
