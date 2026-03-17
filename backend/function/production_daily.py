from flask import Blueprint, jsonify, request

from backend.function.common.decorators import login_required
from backend.services.production_service import (
    ProductionServiceError,
    create_daily_machine_plan,
    create_daily_product_tonnage,
    delete_daily_machine_plan,
    delete_daily_product_tonnage,
    get_month_machine_plan_records,
    get_month_product_tonnage_records,
    parse_iso_date,
    parse_year_month,
    update_daily_machine_plan,
    update_daily_product_tonnage,
)
from backend.models import DailyMachinePlan, DailyProductTonnage

production_daily_bp = Blueprint("production_daily", __name__)


def _service_response(action, success_message, success_status=200):
    try:
        item = action()
        payload = {"message": success_message}
        if item is not None:
            payload["item"] = item.to_dict()
        return jsonify(payload), success_status
    except ProductionServiceError as exc:
        return jsonify({"message": exc.message}), exc.status_code
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 400


@production_daily_bp.get("/daily-production")
@login_required
def get_daily_production(current_user):
    date_value = request.args.get("date")
    month_value = request.args.get("month")

    try:
        if date_value:
            record_date = parse_iso_date(date_value)
            records = (
                DailyProductTonnage.query.filter_by(record_date=record_date)
                .order_by(DailyProductTonnage.product_id.asc())
                .all()
            )
            return jsonify({"items": [item.to_dict() for item in records]})

        if month_value:
            year, month = parse_year_month(month_value)
            records = get_month_product_tonnage_records(year, month)
            return jsonify({"items": [item.to_dict() for item in records]})
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 400

    return jsonify({"message": "date or month query parameter is required"}), 400


@production_daily_bp.post("/daily-production")
@login_required
def post_daily_production(current_user):
    payload = request.get_json(silent=True) or {}
    return _service_response(lambda: create_daily_product_tonnage(payload), "Daily production created", 201)


@production_daily_bp.put("/daily-production/<int:record_id>")
@login_required
def put_daily_production(record_id, current_user):
    payload = request.get_json(silent=True) or {}
    return _service_response(lambda: update_daily_product_tonnage(record_id, payload), "Daily production updated")


@production_daily_bp.delete("/daily-production/<int:record_id>")
@login_required
def remove_daily_production(record_id, current_user):
    return _service_response(lambda: delete_daily_product_tonnage(record_id), "Daily production deleted")


@production_daily_bp.get("/daily-machine-plans")
@login_required
def get_daily_machine_plans(current_user):
    date_value = request.args.get("date")
    month_value = request.args.get("month")

    try:
        if date_value:
            record_date = parse_iso_date(date_value)
            records = (
                DailyMachinePlan.query.filter_by(plan_date=record_date)
                .order_by(DailyMachinePlan.machine_id.asc())
                .all()
            )
            return jsonify({"items": [item.to_dict() for item in records]})

        if month_value:
            year, month = parse_year_month(month_value)
            records = get_month_machine_plan_records(year, month)
            return jsonify({"items": [item.to_dict() for item in records]})
    except ValueError as exc:
        return jsonify({"message": str(exc)}), 400

    return jsonify({"message": "date or month query parameter is required"}), 400


@production_daily_bp.post("/daily-machine-plans")
@login_required
def post_daily_machine_plan(current_user):
    payload = request.get_json(silent=True) or {}
    return _service_response(lambda: create_daily_machine_plan(payload), "Daily machine plan created", 201)


@production_daily_bp.put("/daily-machine-plans/<int:record_id>")
@login_required
def put_daily_machine_plan(record_id, current_user):
    payload = request.get_json(silent=True) or {}
    return _service_response(lambda: update_daily_machine_plan(record_id, payload), "Daily machine plan updated")


@production_daily_bp.delete("/daily-machine-plans/<int:record_id>")
@login_required
def remove_daily_machine_plan(record_id, current_user):
    return _service_response(lambda: delete_daily_machine_plan(record_id), "Daily machine plan deleted")


@production_daily_bp.get("/daily-breakdowns")
@login_required
def get_daily_breakdowns(current_user):
    return jsonify({"message": "Legacy breakdown module removed from raw-data schema"}), 410


@production_daily_bp.post("/daily-breakdowns")
@login_required
def create_daily_breakdown(current_user):
    return jsonify({"message": "Legacy breakdown module removed from raw-data schema"}), 410


@production_daily_bp.put("/daily-breakdowns/<int:record_id>")
@login_required
def update_daily_breakdown(record_id, current_user):
    return jsonify({"message": "Legacy breakdown module removed from raw-data schema"}), 410


@production_daily_bp.delete("/daily-breakdowns/<int:record_id>")
@login_required
def delete_daily_breakdown(record_id, current_user):
    return jsonify({"message": "Legacy breakdown module removed from raw-data schema"}), 410
