from flask import Blueprint, jsonify

from backend.function.common.decorators import login_required

production_bp = Blueprint("production", __name__)


@production_bp.get("")
@login_required
def production_home(current_user):
    return jsonify(
        {
            "message": "Production API is running",
            "user": current_user.to_dict(),
        }
    )
