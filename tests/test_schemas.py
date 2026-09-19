import unittest
from datetime import UTC, datetime

from pydantic import ValidationError

from app.models import BackupResult
from app.schemas import BackupCreate


class BackupSchemaTests(unittest.TestCase):
    def test_failed_backup_requires_message(self) -> None:
        with self.assertRaises(ValidationError):
            BackupCreate(
                result=BackupResult.failed,
                started_at=datetime(2026, 9, 19, 10, 0, tzinfo=UTC),
                completed_at=datetime(2026, 9, 19, 10, 5, tzinfo=UTC),
            )

    def test_completion_must_not_precede_start(self) -> None:
        with self.assertRaises(ValidationError):
            BackupCreate(
                result=BackupResult.success,
                started_at=datetime(2026, 9, 19, 10, 5, tzinfo=UTC),
                completed_at=datetime(2026, 9, 19, 10, 0, tzinfo=UTC),
            )


if __name__ == "__main__":
    unittest.main()
