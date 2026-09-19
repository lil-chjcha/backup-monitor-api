from datetime import UTC, datetime, timedelta

from app.models import BackupResult
from app.schemas import BackupState


def normalize_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def evaluate_backup_state(
    *,
    last_result: BackupResult | None,
    last_completed_at: datetime | None,
    expected_interval_hours: int,
    now: datetime | None = None,
) -> BackupState:
    if last_result is None or last_completed_at is None:
        return BackupState.missing
    if last_result == BackupResult.failed:
        return BackupState.failed

    current_time = normalize_utc(now or datetime.now(UTC))
    completed_at = normalize_utc(last_completed_at)
    deadline = completed_at + timedelta(hours=expected_interval_hours)
    return BackupState.overdue if current_time > deadline else BackupState.healthy
