from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.store import Store
from app.auth.dependencies import get_current_user, require_roles
from app.models.user import User

from app.schemas.store_update import StoreUpdateRequest

from fastapi import UploadFile, File
import csv
from io import StringIO
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter(prefix="/api/admin/stores", tags=["Admin Stores"])

def serialize_store(s: Store):
    return {
        "store_id": s.store_id,
        "name": s.name,
        "store_type": s.store_type,
        "status": s.status,
        "latitude": s.latitude,
        "longitude": s.longitude,
        "address": {
            "street": s.address_street,
            "city": s.address_city,
            "state": s.address_state,
            "postal_code": s.address_postal_code,
            "country": s.address_country,
        },
        "phone": s.phone,
        "services": s.services.split("|") if s.services else [],
        "hours": {
            "mon": s.hours_mon,
            "tue": s.hours_tue,
            "wed": s.hours_wed,
            "thu": s.hours_thu,
            "fri": s.hours_fri,
            "sat": s.hours_sat,
            "sun": s.hours_sun,
        },
    }


@router.get("")
def list_stores(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "marketer")),
):
    total_stores = db.query(Store).count()
    stores = db.query(Store).limit(total_stores).all()

    return {
        "total":total_stores,
        "stores": [serialize_store(s) for s in stores]
    }

@router.get("/{store_id}")
def get_store_detail(
    store_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    store = db.query(Store).filter(Store.store_id == store_id).first()

    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    return serialize_store(store)


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
        raise HTTPException(status_code=404, detail="Store not found")
        # return {"error": "Store not found"}, 404

    update_data = body.dict(exclude_unset=True)

    # Handle services list → string
    if "services" in update_data:
        update_data["services"] = "|".join(update_data["services"])

    # check if update_data is empty
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields provided for update. Fields allowed for update: name, store_type, latitude, longitude, address (street, city, state, postal_code, country), phone, services (list of strings), hours (mon, tue, wed, thu, fri, sat, sun)")
        # return {"message": "No valid fields provided for update. Fields allowed for update:
        # raise HTTPException(status_code=404, 
        # detail="Fields to update could be invalid or missing. No updates applied. Fields allowed for update: name, store_type, latitude, longitude, address (street, city, state, postal_code, country), phone, services (list of strings), hours (mon, tue, wed, thu, fri, sat, sun)")
        # return {"message": "Fields to update could be invalid or missing. No updates applied. Fields allowed for update: name, store_type, latitude, longitude, address (street, city, state, postal_code, country), phone, services (list of strings), hours (mon, tue, wed, thu, fri, sat, sun)"}, 400

    # for field in update_data.keys():
    #     if field not in StoreUpdateRequest.__fields__:
    #         return {"error": f"Invalid field included: {field}, not allowed for update"}, 400

    # Apply updates
    updated_fields = []
    for field, value in update_data.items():
        # update only if value is not None (allows partial updates) 
        # and field exists on the model 
        # and different from current value
        if value is not None and hasattr(store, field) and getattr(store, field) != value:
            updated_fields.append(field)
            setattr(store, field, value)

    db.commit()

    return {
        "message": "Store updated",
        "store_id": store_id,
        "updated_fields": updated_fields,
    }


@router.post("/import")
def import_stores_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "marketer")),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be CSV")

    content = file.file.read().decode("utf-8")
    reader = csv.DictReader(StringIO(content))

    required_fields = {"store_id", "name", "store_type", "status", "latitude", "longitude"}

    if not required_fields.issubset(set(reader.fieldnames)):
        raise HTTPException(status_code=400, detail="Invalid CSV headers")

    created = 0
    updated = 0
    failed = []

    try:
        for i, row in enumerate(reader, start=2):  # header = row 1
            try:
                store_id = row["store_id"]

                # basic validation
                if not store_id or not row["name"]:
                    raise ValueError("Missing required fields")

                lat_str = float(row["latitude"])
                lon_str = float(row["longitude"])

                lat = float(lat_str) if lat_str else None
                lon = float(lon_str) if lon_str else None

                # AUTO GEOCODE if missing
                if lat is None or lon is None:
                    geo = None

                    if row.get("postal_code"):
                        geo = geocode_postal_code(row["postal_code"])

                    elif row.get("address_street"):
                        address = f"{row.get('address_street','')}, {row.get('address_city','')}, {row.get('address_state','')}"
                        geo = geocode_address(address)

                    if not geo:
                        raise ValueError("Missing coordinates and unable to geocode")

                    lat = geo["latitude"]
                    lon = geo["longitude"]
                    
                # Validate range of lat/lon
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    raise ValueError("Invalid coordinates")

                store = db.query(Store).filter(Store.store_id == store_id).first()

                services = row.get("services", "")
                services_str = services if isinstance(services, str) else "|".join(services)

                if store:
                    # UPDATE
                    store.name = row["name"]
                    store.store_type = row["store_type"]
                    store.status = row["status"]
                    store.latitude = lat
                    store.longitude = lon
                    store.services = services_str

                    updated += 1
                else:
                    # CREATE
                    store = Store(
                        store_id=store_id,
                        name=row["name"],
                        store_type=row["store_type"],
                        status=row["status"],
                        latitude=lat,
                        longitude=lon,
                        services=services_str,
                    )
                    db.add(store)
                    created += 1

            except Exception as e:
                failed.append({
                    "row": i,
                    "error": str(e),
                })

        if failed:
            db.rollback()
            return {
                "status": "failed",
                "total": created + updated + len(failed),
                "created": created,
                "updated": updated,
                "failed": failed,
            }

        db.commit()

    except SQLAlchemyError:
        db.rollback() # all or nothing - if any error occurs, rollback entire transaction to avoid partial updates
        raise HTTPException(status_code=500, detail="Batch CSV Import failed due to database error")

    return {
        "status": "success",
        "total": created + updated,
        "created": created,
        "updated": updated,
        "failed": [],
    }