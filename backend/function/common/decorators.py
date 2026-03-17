from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from backend.models import UserData


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({"message": "Authentication required"}), 401

        user_id = get_jwt_identity()
        try:
            user = UserData.query.get(int(user_id))
        except (TypeError, ValueError):
            user = None
        if user is None or not user.is_active:
            return jsonify({"message": "Invalid user"}), 401

        return func(*args, current_user=user, **kwargs)

    return wrapper
