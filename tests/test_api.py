import os
import unittest

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"

from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


class ApiFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_server_backup_and_dashboard_flow(self) -> None:
        with TestClient(app) as client:
            created = client.post(
                "/api/v1/servers",
                json={
                    "name": "proxmox-node-1",
                    "host": "10.0.0.10",
                    "environment": "homelab",
                    "expected_interval_hours": 168,
                },
            )
            self.assertEqual(created.status_code, 201)
            server = created.json()
            self.assertEqual(server["backup_state"], "missing")

            reported = client.post(
                f"/api/v1/servers/{server['id']}/backups",
                json={
                    "result": "success",
                    "started_at": "2026-09-19T01:00:00Z",
                    "completed_at": "2026-09-19T01:15:00Z",
                    "size_mb": 512.4,
                },
            )
            self.assertEqual(reported.status_code, 201)

            summary = client.get("/api/v1/dashboard/summary")
            self.assertEqual(summary.status_code, 200)
            self.assertEqual(summary.json()["total_servers"], 1)

    def test_duplicate_server_name_returns_conflict(self) -> None:
        payload = {"name": "unique-node", "host": "node.local"}
        with TestClient(app) as client:
            self.assertEqual(client.post("/api/v1/servers", json=payload).status_code, 201)
            self.assertEqual(client.post("/api/v1/servers", json=payload).status_code, 409)


if __name__ == "__main__":
    unittest.main()
