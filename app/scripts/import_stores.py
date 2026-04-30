import csv
from app.db.database import SessionLocal
from app.models.store import Store


def import_stores(csv_file_path: str):
    db = SessionLocal()

    created = 0
    updated = 0
    failed = []

    try:
        with open(csv_file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row_number, row in enumerate(reader, start=2):
                try:
                    store_id = row["store_id"]

                    store = db.query(Store).filter(Store.store_id == store_id).first()

                    data = {
                        "name": row["name"],
                        "store_type": row["store_type"],
                        "status": row["status"],
                        "latitude": float(row["latitude"]),
                        "longitude": float(row["longitude"]),
                        "address_street": row["address_street"],
                        "address_city": row["address_city"],
                        "address_state": row["address_state"],
                        "address_postal_code": row["address_postal_code"],
                        "address_country": row["address_country"],
                        "phone": row["phone"],
                        "services": row["services"],
                        "hours_mon": row["hours_mon"],
                        "hours_tue": row["hours_tue"],
                        "hours_wed": row["hours_wed"],
                        "hours_thu": row["hours_thu"],
                        "hours_fri": row["hours_fri"],
                        "hours_sat": row["hours_sat"],
                        "hours_sun": row["hours_sun"],
                    }

                    if store:
                        for key, value in data.items():
                            setattr(store, key, value)
                        updated += 1
                    else:
                        store = Store(store_id=store_id, **data)
                        db.add(store)
                        created += 1

                except Exception as e:
                    failed.append({
                        "row": row_number,
                        "store_id": row.get("store_id"),
                        "error": str(e),
                    })

        if failed:
            db.rollback()
            return {
                "status": "failed",
                "message": "Import rolled back due to row errors",
                "created": 0,
                "updated": 0,
                "failed": failed,
            }

        print(f"Imported stores: {created} created, {updated} updated, {len(failed)} failed")    

        db.commit()

        return {
            "status": "success",
            "created": created,
            "updated": updated,
            "failed": [],
        }

    except Exception as e:
        db.rollback()
        return {
            "status": "failed",
            "error": str(e),
        }

    finally:
        db.close()


if __name__ == "__main__":
    report = import_stores("data/stores_50.csv")
    print(report)