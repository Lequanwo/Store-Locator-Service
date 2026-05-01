# 🗺️ Store Locator API

A production-ready **Store Locator backend service** built with FastAPI and PostgreSQL.  
Supports geospatial search, authentication, admin operations, and scalable API design.

---

## Live Demo

- **Base URL:**  
  https://store-locator-service-a800.onrender.com

- **Swagger Docs:**  
  https://store-locator-service-a800.onrender.com/docs

---

## Features

### 🔍 Store Search
- Search by:
  - Latitude & Longitude
  - Postal Code
  - Address (geocoding)
- Radius-based filtering (miles)
- Filter by:
  - Store types
  - Services (AND logic)
- Optimized using **bounding box + exact distance calculation**
- Sorted by nearest distance

---

### Authentication & Authorization
- JWT-based authentication
- Endpoints:
  - Login
  - Refresh token
  - Logout
- Role-based access control (RBAC)
  - Admin-only endpoints

---

### Admin Features
- List stores
- Update store (PATCH)
- Soft delete store
- CSV import with **upsert logic**

---

### Performance & Reliability
- Rate limiting (SlowAPI)
- Bounding box optimization for geospatial queries
- Production deployment on Render

---

### Testing
- Unit tests:
  - Distance calculation
  - Bounding box
  - Password hashing
- API tests:
  - Search endpoint
  - Auth flow
  - Admin endpoints

---

## Tech Stack

- **Backend:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Auth:** JWT (PyJWT)
- **Geolocation:** Geopy
- **Rate Limiting:** SlowAPI
- **Deployment:** Render

---

## Project Structure
app/
├── api/ # API routes
├── auth/ # Authentication logic
├── db/ # Database setup
├── models/ # SQLAlchemy models
├── schemas/ # Pydantic schemas
├── services/ # Business logic
├── scripts/ # Seed & CSV import
└── main.py # App entry point

tests/ # Test suite
data/ # CSV data


---

## Setup (Local)

### 1. Clone repo

git clone https://github.com/your-username/store-locator-service.git
cd store-locator-service

### 2. Install dependencies
pip install -r requirements.txt

### 3. Create .env
DATABASE_URL=postgresql://user:password@localhost:5432/store_locator
SECRET_KEY=your-secret-key
ENV=development

### 4. Run server
uvicorn app.main:app --reload

## Example API Usage

### Search Stores

POST /api/stores/search
{
  "postal_code": "02101",
  "radius_miles": 20,
  "store_types": ["outlet"],
  "services": ["pickup"]
}

### Login

POST /api/auth/login
{
  "email": "admin@test.com",
  "password": "AdminTest123!"
}
### Admin (Protected)

GET /api/admin/stores
Authorization: Bearer <token>

## Design Highlights
Geospatial Optimization
Bounding box reduces DB scan
Exact distance computed only on candidates
Scalable Architecture
Separation of concerns (API / service / DB)
Dependency injection for DB session
Security
JWT auth
Role-based access control
Data Pipeline
CSV import with upsert
Idempotent seed scripts


## Running Tests
pytest -v

## Deployment

Deployed on Render:

Web Service (FastAPI)
Managed PostgreSQL

Environment variables configured via Render dashboard.

## Future Improvements
Pagination for search results
Redis caching for search queries
PostGIS integration for geospatial queries
Async database support
Observability (metrics & logging)

## Author

Lequan Wang

## 