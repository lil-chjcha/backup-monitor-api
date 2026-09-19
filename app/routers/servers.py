from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import BackupEvent, Server
from app.schemas import ServerCreate, ServerRead, ServerStatus
from app.services import evaluate_backup_state

router = APIRouter(prefix="/servers", tags=["servers"])
DatabaseSession = Annotated[Session, Depends(get_db)]
ActiveOnly = Annotated[bool, Query()]


def build_server_status(db: Session, server: Server) -> ServerStatus:
    latest = db.scalar(
        select(BackupEvent)
        .where(BackupEvent.server_id == server.id)
        .order_by(BackupEvent.completed_at.desc())
        .limit(1)
    )
    return ServerStatus(
        **ServerRead.model_validate(server).model_dump(),
        backup_state=evaluate_backup_state(
            last_result=latest.result if latest else None,
            last_completed_at=latest.completed_at if latest else None,
            expected_interval_hours=server.expected_interval_hours,
        ),
        last_backup_at=latest.completed_at if latest else None,
    )


@router.post("", response_model=ServerStatus, status_code=status.HTTP_201_CREATED)
def create_server(payload: ServerCreate, db: DatabaseSession) -> ServerStatus:
    server = Server(**payload.model_dump())
    db.add(server)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A server with this name already exists",
        ) from exc
    db.refresh(server)
    return build_server_status(db, server)


@router.get("", response_model=list[ServerStatus])
def list_servers(db: DatabaseSession, active_only: ActiveOnly = True) -> list[ServerStatus]:
    statement = select(Server).order_by(Server.name)
    if active_only:
        statement = statement.where(Server.active.is_(True))
    return [build_server_status(db, server) for server in db.scalars(statement).all()]


@router.get("/{server_id}", response_model=ServerStatus)
def get_server(server_id: int, db: DatabaseSession) -> ServerStatus:
    server = db.get(Server, server_id)
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return build_server_status(db, server)
