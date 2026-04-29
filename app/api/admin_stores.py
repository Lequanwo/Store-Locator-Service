from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.store import Store
from app.auth.dependencies import get_current_user, require_roles
from app.models.user import User

from app.schemas.store_update import StoreUpdateRequest

router = APIRouter(prefix="/api/admin/stores", tags=["Admin Stores"])


@router.get("")
def list_stores(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stores = db.query(Store).limit(50).all()

    return [
        {
            "store_id": s.store_id,
            "name": s.name,
            "store_type": s.store_type,
            "status": s.status,
            "latitude": s.latitude,
            "longitude": s.longitude,
        }
        for s in stores
    ]


@router.delete("/{store_id}")
def deactivate_store(
    store_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "marketer")),
):
    store = db.query(Store).filter(Store.store_id == store_id).first()

    if not store:
        return {"error": "Store not found"}

    store.status = "inactive"
    db.commit()

    return {"message": "Store deactivated", "store_id": store_id}


@router.patch("/{store_id}")
def update_store(
    store_id: str,
    body: StoreUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "marketer")),
):
    store = db.query(Store).filter(Store.store_id == store_id).first()

    if not store:
        return {"error": "Store not found"}

    update_data = body.dict(exclude_unset=True)

    # Handle services list → string
    if "services" in update_data:
        update_data["services"] = "|".join(update_data["services"])

    # Apply updates
    for field, value in update_data.items():
        setattr(store, field, value)

    db.commit()

    return {
        "message": "Store updated",
        "store_id": store_id,
        "updated_fields": list(update_data.keys())
    }