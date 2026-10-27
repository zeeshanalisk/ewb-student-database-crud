from fastapi.testclient import TestClient

from app import database
from app.main import app


def test_student_crud_and_filtering(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test_students.db")

    with TestClient(app) as client:
        create = client.post(
            "/students",
            json={
                "name": "Test Student",
                "date_of_birth": "2005-06-15",
                "email": "test.student@example.com",
                "course": "BCA",
            },
        )
        assert create.status_code == 201
        student = create.json()
        student_id = student["student_id"]
        assert student["name"] == "Test Student"

        listing = client.get("/students?course=BCA")
        assert listing.status_code == 200
        assert len(listing.json()) == 1

        partial_update = client.patch(f"/students/{student_id}", json={"course": "BCA Honours"})
        assert partial_update.status_code == 200
        assert partial_update.json()["course"] == "BCA Honours"

        get_one = client.get(f"/students/{student_id}")
        assert get_one.status_code == 200
        assert get_one.json()["name"] == "Test Student"

        delete = client.delete(f"/students/{student_id}")
        assert delete.status_code == 204
        missing = client.get(f"/students/{student_id}")
        assert missing.status_code == 404


def test_contact_detail_is_required(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test_students.db")

    with TestClient(app) as client:
        response = client.post(
            "/students",
            json={"name": "No Contact", "date_of_birth": "2005-06-15"},
        )
        assert response.status_code == 422
