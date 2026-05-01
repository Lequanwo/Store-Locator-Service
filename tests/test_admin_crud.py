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

def test_create_store():
    token = get_admin_token()

    response = client.post(
        "/api/admin/stores",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "store_id": "S9000",
            "name": "Test Store 22",
            "store_type": "grocery",
            "status": "active",
            "latitude": 40,
            "longitude": -74,
            "address_street": "123 Test St",
            "address_city": "Tes",
            "address_state": "TS",
            "address_postal_code": "1234",
            "address_country": "Tes",
            "phone": "5551234567",
            "services": ["pickup", "delivery"],
            "hours_mon": "9am-9pm",
            "hours_tue": "9am-9pm",
            "hours_wed": "9am-9pm",
            "hours_thu": "9am-9pm",
            "hours_fri": "9am-10pm",
            "hours_sat": "10am-10pm",
            "hours_sun": "10am-8pm"
        },
    )

    assert response.status_code == 200
    assert response.json()["store_id"] == "S9000"

    # Cleanup - delete the created store
    response_delete = client.delete(
        "/api/admin/stores/S9000",
        headers={"Authorization": f"Bearer {token}"}
    )
    # assert response_delete.status_code == 200
    # assert with message
    assert response_delete.json()["message"] == "Store deactivated"

def test_get_store_detail():
    token = get_admin_token()

    response = client.get(
        "/api/admin/stores/S9999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["store_id"] == "S9999"

def test_patch_store_name():
    token = get_admin_token()
    
    response = client.patch(
        "/api/admin/stores/S9999",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Updated Test Store 22"
        },
    )
    print(response.json())

    assert response.status_code == 200
    assert "name" in response.json()["updated_fields"]


def test_patch_store_services():
    token = get_admin_token()

    response = client.patch(
        "/api/admin/stores/S9999",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "services": ["pickup", "pharmacy", "grocery"],
            "hours_mon": "8am-8pm",
            "hours_tue": "8am-8pm",
        },
    )

    assert response.status_code == 200
    assert "services" in response.json()["updated_fields"]
    assert "hours_mon" in response.json()["updated_fields"]
    assert "hours_tue" in response.json()["updated_fields"]
    # assert response.json()["updated_fields"]["services"] == ["pickup", "pharmacy", "grocery"]
    assert "name" not in response.json()["updated_fields"]


def test_delete_store_soft_delete():
    token = get_admin_token()

    response = client.delete(
        "/api/admin/stores/S9999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code in [200, 404]

def test_list_stores():
    token = get_admin_token()

    response = client.get(
        "/api/admin/stores",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert "total" in response.json()
    assert "stores" in response.json()
    assert isinstance(response.json()["stores"], list)
    assert len(response.json()["stores"]) >= 0

