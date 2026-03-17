from flask import Blueprint, jsonify

from backend.function.common.decorators import login_required

auth_bp = Blueprint("current_user", __name__)


@auth_bp.get("/me")
@login_required
def current_user(current_user):
    return jsonify({"user": current_user.to_dict()})
