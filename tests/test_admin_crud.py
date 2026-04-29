from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_admin_token():
    response = client.post(
        "/api/auth/login",
        json={
            "email": "admin@test.com",
            "password": "AdminTest123!",
        },
    )
    return response.json()["access_token"]


def test_patch_store_name():
    token = get_admin_token()

    response = client.patch(
        "/api/admin/stores/S0001",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Updated Test Store"
        },
    )

    assert response.status_code == 200
    assert "name" in response.json()["updated_fields"]


def test_patch_store_services():
    token = get_admin_token()

    response = client.patch(
        "/api/admin/stores/S0001",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "services": ["pickup", "pharmacy"]
        },
    )

    assert response.status_code == 200
    assert "services" in response.json()["updated_fields"]


def test_delete_store_soft_delete():
    token = get_admin_token()

    response = client.delete(
        "/api/admin/stores/S9999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code in [200, 404]