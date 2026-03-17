from datetime import datetime

from flask import Blueprint, jsonify, request

from backend.function.common.decorators import login_required
from backend.models import DailyMachinePlan, DailyProductTonnage
from backend.models.db import db
from backend.services.production_service import (
    get_month_machine_plan_records,
    get_month_product_tonnage_records,
    parse_iso_date,
    parse_year_month,
)

production_daily_bp = Blueprint("production_daily", __name__)


def _decimal_number(payload, key, required=False, allow_zero=True):
    raw_value = payload.get(key)
    if raw_value in (None, ""):
        if required:
            raise ValueError(f"{key} is required")
        return 0
    value = float(raw_value)
    if value < 0 or (not allow_zero and value <= 0):
        comparator = "> 0" if not allow_zero else ">= 0"
        raise ValueError(f"{key} must be {comparator}")
    return value


@production_daily_bp.get("/daily-production")
@login_required
def get_daily_production(current_user):
    date_value = request.args.get("date")
    month_value = request.args.get("month")

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

    return jsonify({"message": "date or month query parameter is required"}), 400


@production_daily_bp.post("/daily-production")
@login_required
def create_daily_production(current_user):
    payload = request.get_json(silent=True) or {}

    try:
        record_date = parse_iso_date(payload.get("record_date"))
        product_id = int(payload.get("product_id") or 0)
        output_mt = _decimal_number(payload, "output_mt")
    except (TypeError, ValueError) as error:
        return jsonify({"message": str(error)}), 400

    if product_id <= 0:
        return jsonify({"message": "product_id is required"}), 400

    duplicate = DailyProductTonnage.query.filter_by(
        record_date=record_date,
        product_id=product_id,
    ).first()
    if duplicate:
        return jsonify({"message": "Daily production record already exists for this product and date"}), 409

    record = DailyProductTonnage(
        record_date=record_date,
        product_id=product_id,
        output_mt=output_mt,
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({"message": "Daily production created", "item": record.to_dict()}), 201


@production_daily_bp.put("/daily-production/<int:record_id>")
@login_required
def update_daily_production(record_id, current_user):
    record = DailyProductTonnage.query.get_or_404(record_id)
    payload = request.get_json(silent=True) or {}

    try:
        record_date = parse_iso_date(payload.get("record_date") or record.record_date.isoformat())
        product_id = int(payload.get("product_id") or record.product_id)
        record.output_mt = _decimal_number(payload, "output_mt")
    except (TypeError, ValueError) as error:
        return jsonify({"message": str(error)}), 400

    duplicate = DailyProductTonnage.query.filter(
        DailyProductTonnage.record_date == record_date,
        DailyProductTonnage.product_id == product_id,
        DailyProductTonnage.id != record_id,
    ).first()
    if duplicate:
        return jsonify({"message": "Daily production record already exists for this product and date"}), 409

    record.record_date = record_date
    record.product_id = product_id
    db.session.commit()
    return jsonify({"message": "Daily production updated", "item": record.to_dict()})


@production_daily_bp.delete("/daily-production/<int:record_id>")
@login_required
def delete_daily_production(record_id, current_user):
    record = DailyProductTonnage.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": "Daily production deleted"})


@production_daily_bp.get("/daily-machine-plans")
@login_required
def get_daily_machine_plans(current_user):
    date_value = request.args.get("date")
    month_value = request.args.get("month")

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

    return jsonify({"message": "date or month query parameter is required"}), 400


@production_daily_bp.post("/daily-machine-plans")
@login_required
def create_daily_machine_plan(current_user):
    payload = request.get_json(silent=True) or {}

    try:
        plan_date = parse_iso_date(payload.get("plan_date"))
        machine_id = int(payload.get("machine_id") or 0)
        planned_output_mt = _decimal_number(payload, "planned_output_mt")
        standard_output_mt = payload.get("standard_output_mt")
        standard_output_mt = None if standard_output_mt in (None, "") else float(standard_output_mt)
    except (TypeError, ValueError) as error:
        return jsonify({"message": str(error)}), 400

    if machine_id <= 0:
        return jsonify({"message": "machine_id is required"}), 400

    duplicate = DailyMachinePlan.query.filter_by(plan_date=plan_date, machine_id=machine_id).first()
    if duplicate:
        return jsonify({"message": "Daily machine plan already exists for this machine and date"}), 409

    record = DailyMachinePlan(
        plan_date=plan_date,
        machine_id=machine_id,
        planned_output_mt=planned_output_mt,
        standard_output_mt=standard_output_mt,
    )
    db.session.add(record)
    db.session.commit()
    return jsonify({"message": "Daily machine plan created", "item": record.to_dict()}), 201


@production_daily_bp.put("/daily-machine-plans/<int:record_id>")
@login_required
def update_daily_machine_plan(record_id, current_user):
    record = DailyMachinePlan.query.get_or_404(record_id)
    payload = request.get_json(silent=True) or {}

    try:
        plan_date = parse_iso_date(payload.get("plan_date") or record.plan_date.isoformat())
        machine_id = int(payload.get("machine_id") or record.machine_id)
        record.planned_output_mt = _decimal_number(payload, "planned_output_mt")
        standard_output_mt = payload.get("standard_output_mt", record.standard_output_mt)
        record.standard_output_mt = None if standard_output_mt in (None, "") else float(standard_output_mt)
    except (TypeError, ValueError) as error:
        return jsonify({"message": str(error)}), 400

    duplicate = DailyMachinePlan.query.filter(
        DailyMachinePlan.plan_date == plan_date,
        DailyMachinePlan.machine_id == machine_id,
        DailyMachinePlan.id != record_id,
    ).first()
    if duplicate:
        return jsonify({"message": "Daily machine plan already exists for this machine and date"}), 409

    record.plan_date = plan_date
    record.machine_id = machine_id
    db.session.commit()
    return jsonify({"message": "Daily machine plan updated", "item": record.to_dict()})


@production_daily_bp.delete("/daily-machine-plans/<int:record_id>")
@login_required
def delete_daily_machine_plan(record_id, current_user):
    record = DailyMachinePlan.query.get_or_404(record_id)
    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": "Daily machine plan deleted"})


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
