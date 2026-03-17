from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash

from backend.models import UserData

login_bp = Blueprint("login", __name__)


@login_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""

    if not username or not password:
        return jsonify({"message": "username and password are required"}), 400

    user = UserData.query.filter_by(username=username).first()
    if user is None or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid username or password"}), 401

    if not user.is_active:
        return jsonify({"message": "User is inactive"}), 403

    access_token = create_access_token(identity=str(user.id))
    return jsonify(
        {
            "access_token": access_token,
            "user": user.to_dict(),
        }
    )
