from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.auth.dependencies import require_roles
from app.auth.security import hash_password
from app.schemas.user_admin import UserCreateRequest, UserUpdateRequest

router = APIRouter(prefix="/api/admin/users", tags=["Admin Users"])

ALLOWED_ROLES = {"marketer", "viewer"}


def serialize_user(user: User):
    return {
        "user_id": user.user_id,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
    }


@router.post("")
def create_user(
    body: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    if body.role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    existing = db.query(User).filter(
        (User.user_id == body.user_id) | (User.email == body.email)
    ).first()

    if existing:
        print(f"User creation failed: user_id {body.user_id} or email {body.email} already exists")
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        user_id=body.user_id,
        email=body.email,
        password_hash=hash_password(body.password),
        role=body.role,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return serialize_user(user)


@router.get("")
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    users = db.query(User).all()
    return [serialize_user(u) for u in users]


@router.put("/{user_id}")
def update_user(
    user_id: str,
    body: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = body.dict(exclude_unset=True)

    # check if empty update
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    if "role" in update_data:
        if update_data["role"] not in ALLOWED_ROLES:
            raise HTTPException(status_code=400, detail="Invalid role")

    for field, value in update_data.items():
        # no password updates
        if field == "password":
            continue
        setattr(user, field, value)

    db.commit()
    # db.refresh(user)

    return serialize_user(user)


@router.delete("/{user_id}")
def deactivate_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()
    # db.refresh(user)

    return {
        "message": "User deactivated",
        "user": serialize_user(user),
    }