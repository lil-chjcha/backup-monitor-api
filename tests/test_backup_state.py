import unittest
from datetime import UTC, datetime, timedelta

from app.models import BackupResult
from app.schemas import BackupState
from app.services import evaluate_backup_state


class BackupStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 9, 19, 12, 0, tzinfo=UTC)

    def test_missing_when_no_backup_exists(self) -> None:
        result = evaluate_backup_state(
            last_result=None,
            last_completed_at=None,
            expected_interval_hours=168,
            now=self.now,
        )
        self.assertEqual(result, BackupState.missing)

    def test_failed_result_has_priority(self) -> None:
        result = evaluate_backup_state(
            last_result=BackupResult.failed,
            last_completed_at=self.now - timedelta(hours=1),
            expected_interval_hours=168,
            now=self.now,
        )
        self.assertEqual(result, BackupState.failed)

    def test_recent_success_is_healthy(self) -> None:
        result = evaluate_backup_state(
            last_result=BackupResult.success,
            last_completed_at=self.now - timedelta(hours=24),
            expected_interval_hours=168,
            now=self.now,
        )
        self.assertEqual(result, BackupState.healthy)

    def test_old_success_is_overdue(self) -> None:
        result = evaluate_backup_state(
            last_result=BackupResult.success,
            last_completed_at=self.now - timedelta(hours=169),
            expected_interval_hours=168,
            now=self.now,
        )
        self.assertEqual(result, BackupState.overdue)

    def test_naive_database_timestamp_is_treated_as_utc(self) -> None:
        result = evaluate_backup_state(
            last_result=BackupResult.success,
            last_completed_at=datetime(2026, 9, 19, 11, 0),
            expected_interval_hours=2,
            now=self.now,
        )
        self.assertEqual(result, BackupState.healthy)


if __name__ == "__main__":
    unittest.main()
