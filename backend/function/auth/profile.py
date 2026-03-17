from flask import Blueprint, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from backend.function.common.decorators import login_required
from backend.models import UserData
from backend.models.db import db

profile_bp = Blueprint("profile", __name__)


@profile_bp.get("/profile")
@login_required
def get_profile(current_user):
    return jsonify({"user": current_user.to_dict()})


@profile_bp.patch("/profile")
@login_required
def update_profile(current_user):
    payload = request.get_json(silent=True) or {}

    username = (payload.get("username") or "").strip()
    full_name = (payload.get("full_name") or "").strip()
    email = (payload.get("email") or "").strip()
    current_password = payload.get("current_password") or ""
    new_password = payload.get("new_password") or ""

    if not username:
        return jsonify({"message": "username is required"}), 400

    if not full_name:
        return jsonify({"message": "full_name is required"}), 400

    username_owner = UserData.query.filter_by(username=username).first()
    if username_owner and username_owner.id != current_user.id:
        return jsonify({"message": "Username is already in use"}), 409

    if email:
        email_owner = UserData.query.filter_by(email=email).first()
        if email_owner and email_owner.id != current_user.id:
            return jsonify({"message": "Email is already in use"}), 409

    if current_password or new_password:
        if not current_password or not new_password:
            return jsonify(
                {"message": "current_password and new_password are required"},
            ), 400

        if len(new_password) < 6:
            return jsonify(
                {"message": "new_password must be at least 6 characters"},
            ), 400

        if not check_password_hash(current_user.password_hash, current_password):
            return jsonify({"message": "Current password is incorrect"}), 400

        current_user.password_hash = generate_password_hash(new_password)

    current_user.username = username
    current_user.full_name = full_name
    current_user.email = email or None

    db.session.commit()

    return jsonify(
        {
            "message": "Profile updated successfully",
            "user": current_user.to_dict(),
        }
    )
