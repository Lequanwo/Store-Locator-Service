from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_admin_login():
    response = client.post(
        "/api/auth/login",
        json={
            "email": "admin@test.com",
            "password": "AdminTest123!",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password():
    response = client.post(
        "/api/auth/login",
        json={
            "email": "admin@test.com",
            "password": "WrongPassword",
        },
    )

    assert response.status_code == 401

def test_login_nonexistent_user():
    response = client.post(
        "/api/auth/login",
        json={
            "email": "fake@test.com",
            "password": "AdminTest123!",
        },
    )

    assert response.status_code == 401

def test_refresh_token_flow():
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "admin@test.com",
            "password": "AdminTest123!",
        },
    )

    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()

def test_logout_refresh_token():
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "admin@test.com",
            "password": "AdminTest123!",
        },
    )

    refresh_token = login_response.json()["refresh_token"]

    logout_response = client.post(
        "/api/auth/logout",
        json={"refresh_token": refresh_token},
    )

    assert logout_response.status_code == 200

    refresh_response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert refresh_response.status_code == 401