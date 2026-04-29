from fastapi import FastAPI, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.db.database import Base, engine
from app.models.store import Store
from app.api.store_search import router as store_search_router

from app.core.limiter import limiter

from app.models.user import User
from app.models.refresh_token import RefreshToken

from app.api.auth import router as auth_router
from app.api.admin_stores import router as admin_stores_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Store Locator API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(store_search_router)

app.include_router(auth_router)

app.include_router(admin_stores_router)

@app.get("/")
def root():
    return {"message": "Store Locator API is running"}