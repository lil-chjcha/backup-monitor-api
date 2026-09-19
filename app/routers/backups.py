from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BackupEvent, Server
from app.schemas import BackupCreate, BackupRead

router = APIRouter(prefix="/servers/{server_id}/backups", tags=["backups"])
DatabaseSession = Annotated[Session, Depends(get_db)]
ResultLimit = Annotated[int, Query(ge=1, le=100)]


def require_server(db: Session, server_id: int) -> Server:
    server = db.get(Server, server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return server


@router.post("", response_model=BackupRead, status_code=status.HTTP_201_CREATED)
def report_backup(
    server_id: int, payload: BackupCreate, db: DatabaseSession
) -> BackupEvent:
    require_server(db, server_id)
    event = BackupEvent(server_id=server_id, **payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=list[BackupRead])
def list_backups(
    server_id: int,
    db: DatabaseSession,
    limit: ResultLimit = 20,
) -> list[BackupEvent]:
    require_server(db, server_id)
    statement = (
        select(BackupEvent)
        .where(BackupEvent.server_id == server_id)
        .order_by(BackupEvent.completed_at.desc())
        .limit(limit)
    )
    return list(db.scalars(statement).all())
