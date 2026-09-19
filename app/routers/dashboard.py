from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Server
from app.routers.servers import build_server_status
from app.schemas import BackupState, DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(db: DatabaseSession) -> DashboardSummary:
    servers = db.scalars(select(Server).where(Server.active.is_(True))).all()
    states = [build_server_status(db, server).backup_state for server in servers]
    return DashboardSummary(
        total_servers=len(states),
        healthy=states.count(BackupState.healthy),
        overdue=states.count(BackupState.overdue),
        failed=states.count(BackupState.failed),
        missing=states.count(BackupState.missing),
    )
