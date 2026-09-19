from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models import BackupResult


class BackupState(StrEnum):
    healthy = "healthy"
    overdue = "overdue"
    failed = "failed"
    missing = "missing"


class ServerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    host: str = Field(min_length=1, max_length=255)
    environment: str = Field(default="production", min_length=2, max_length=30)
    expected_interval_hours: int = Field(default=168, ge=1, le=8760)


class ServerRead(ServerCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    created_at: datetime


class BackupCreate(BaseModel):
    result: BackupResult
    started_at: datetime
    completed_at: datetime
    size_mb: float | None = Field(default=None, ge=0)
    error_message: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_event(self) -> "BackupCreate":
        if self.completed_at < self.started_at:
            raise ValueError("completed_at must be greater than or equal to started_at")
        if self.result == BackupResult.failed and not self.error_message:
            raise ValueError("error_message is required for failed backups")
        return self


class BackupRead(BackupCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    server_id: int
    created_at: datetime


class ServerStatus(ServerRead):
    backup_state: BackupState
    last_backup_at: datetime | None


class DashboardSummary(BaseModel):
    total_servers: int
    healthy: int
    overdue: int
    failed: int
    missing: int
