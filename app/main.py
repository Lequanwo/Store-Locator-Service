from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.db.database import Base, engine
from app.models.store import Store
from app.models.user import User
from app.models.refresh_token import RefreshToken

from app.api.store_search import router as store_search_router
from app.api.auth import router as auth_router
from app.api.admin_stores import router as admin_stores_router
from app.api.admin_users import router as admin_users_router

from app.core.limiter import limiter
from app.scripts.seed_users import seed_users
from app.scripts.import_stores import import_stores

# clear db and create tables
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        seed_users()
        filename = "data/stores_1000.csv"
        import_stores(filename)
        print("✅ import csv data completed", filename)
        print("✅ Seeded production data")
    except Exception as e:
        print("⚠️ Seeding skipped or failed:", e)

    yield


app = FastAPI(
    title="Store Locator API",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


app.include_router(store_search_router)
app.include_router(auth_router)
app.include_router(admin_stores_router)
app.include_router(admin_users_router)


@app.get("/")
def root():
    return {"message": "Store Locator API is running"}