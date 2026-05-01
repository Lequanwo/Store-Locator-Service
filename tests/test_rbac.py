from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_token(email, password):
    response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    return response.json()["access_token"]


def test_viewer_can_list_stores():
    token = get_token("viewer@test.com", "ViewerTest123!")

    response = client.get(
        "/api/admin/stores",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200


def test_viewer_cannot_delete_store():
    token = get_token("viewer@test.com", "ViewerTest123!")

    response = client.delete(
        "/api/admin/stores/S0002",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_marketer_can_delete_store():
    token = get_token("marketer@test.com", "MarketerTest123!")

    response = client.delete(
        "/api/admin/stores/S0002",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

def test_marketer_cannot_manage_users():
    token = get_token("marketer@test.com", "MarketerTest123!")

    response = client.post(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "user_id": "testuser2",
            "email": "testuser2@example.com",
            "password": "TestUser2123!",
            "role": "viewer",
        }
    )

    assert response.status_code == 403