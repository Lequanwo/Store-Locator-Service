from app.db.database import SessionLocal
from app.models.user import User
from app.auth.security import hash_password


def seed_users():
    db = SessionLocal()

    users = [
        {
            "user_id": "U001",
            "email": "admin@test.com",
            "password": "AdminTest123!",
            "role": "admin",
        },
        {
            "user_id": "U002",
            "email": "marketer@test.com",
            "password": "MarketerTest123!",
            "role": "marketer",
        },
        {
            "user_id": "U003",
            "email": "viewer@test.com",
            "password": "ViewerTest123!",
            "role": "viewer",
        },
        {
            "user_id": "U004",
            "email": "test_viewer@test.com",
            "password": "1234",
            "role": "viewer",
        },
    ]

    for u in users:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if existing:
            continue

        user = User(
            user_id=u["user_id"],
            email=u["email"],
            password_hash=hash_password(u["password"]),
            role=u["role"],
            is_active=True,
        )

        db.add(user)

    db.commit()
    db.close()
    print("Seed users created")


if __name__ == "__main__":
    seed_users()