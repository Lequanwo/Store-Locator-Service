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
    assert response.status_code == 200  # ensure login worked
    data = response.json()
    assert "access_token" in data
    return data["access_token"]

# test create user
#  user_id: str
    email: EmailStr
    password: str
    role: str
def test_create_user():
    token = get_admin_token()

    response = client.post(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "user_id": "testuser1",
            "email": "testuser1@example.com",
            "password": "TestUser123!",
            "role": "viewer",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "testuser1"
    assert data["email"] == "testuser1@example.com"
    assert data["role"] == "viewer"

def test_list_users():
    token = get_admin_token()

    response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(u["user_id"] == "testuser1" for u in data)

def test_update_user():
    token = get_admin_token()

    response = client.put(
        "/api/admin/users/testuser1",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "role": "marketer",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "testuser1"
    assert data["role"] == "marketer"
 
def test_deactivate_user():
    token = get_admin_token()

    response = client.delete(
        "/api/admin/users/testuser1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["user_id"] == "testuser1"
    assert data["user"]["is_active"] == False
