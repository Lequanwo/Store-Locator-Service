from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_store_search_cache():
    response = client.post(
        "/api/stores/search",
        json={
            "postal_code": "32801",
            "radius_miles": 100,
            "open_now": False,
        },
    )


    assert response.status_code == 200
    data = response.json()
    # print(f"Search metadata: {data['metadata']}")
    # check cached response
    # print count
    print('=' * 50)
    print(f"Found {len(data['results'])} stores within 105 miles of '390 Main St':")
    for store in data["results"]:
        print(f"Store ID: {store['store_id']}, Name: {store['name']}, Distance: {store['distance_miles']} miles")
    

# def test_store_search_by_coordinates():
#     response = client.post(
#         "/api/stores/search",
#         json={
#             "latitude": 42.3,
#             "longitude": -71.8,
#             "radius_miles": 20,
#         },
#     )

#     assert response.status_code == 200

#     data = response.json()
#     assert "metadata" in data
#     assert "results" in data

#     res = data['results']
#     if res:
#         print(f"Found {len(res)} stores within 20 miles of (42.3, -71.8):")
#         for store in res:
#             # print store info
#             print(f"Store ID: {store['store_id']}, Name: {store['name']}, Distance: {store['distance_miles']} miles")


# def test_search_missing_location():
#     response = client.post(
#         "/api/stores/search",
#         json={
#             "radius_miles": 10
#         },
#     )

#     assert response.status_code == 400


# def test_search_radius_max_capped():
#     response = client.post(
#         "/api/stores/search",
#         json={
#             "latitude": 42.3,
#             "longitude": -71.8,
#             "radius_miles": 999,
#         },
#     )

#     assert response.status_code == 200
#     assert response.json()["metadata"]["radius_miles"] == 100


# def test_search_with_store_type_filter():
#     response = client.post(
#         "/api/stores/search",
#         json={
#             "latitude": 42.3,
#             "longitude": -71.8,
#             "radius_miles": 50,
#             "store_types": ["regular"],
#         },
#     )

#     assert response.status_code == 200

#     for store in response.json()["results"]:
#         assert store["store_type"] == "regular"


# def test_search_with_services_filter():
#     response = client.post(
#         "/api/stores/search",
#         json={
#             "latitude": 42.3,
#             "longitude": -71.8,
#             "radius_miles": 100,
#             "services": ["pickup"],
#         },
#     )

#     assert response.status_code == 200

#     for store in response.json()["results"]:
#         assert "pickup" in store["services"]
        
        

# def test_admin_stores_requires_auth():
#     response = client.get("/api/admin/stores")
#     assert response.status_code in [401, 403]