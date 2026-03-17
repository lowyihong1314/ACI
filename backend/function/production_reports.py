from flask import Blueprint, jsonify, request

from backend.function.common.decorators import login_required
from backend.services.production_service import (
    build_monthly_machine_summary,
    build_monthly_plant_summary,
    build_ytd_summary,
    parse_year_month,
)

production_reports_bp = Blueprint("production_reports", __name__)


@production_reports_bp.get("/reports/monthly-machine-summary")
@login_required
def monthly_machine_summary(current_user):
    year, month = parse_year_month(request.args.get("month"))
    return jsonify({"items": build_monthly_machine_summary(year, month)})


@production_reports_bp.get("/reports/monthly-plant-summary")
@login_required
def monthly_plant_summary(current_user):
    year, month = parse_year_month(request.args.get("month"))
    return jsonify({"items": build_monthly_plant_summary(year, month)})


@production_reports_bp.get("/reports/breakdown-analysis")
@login_required
def breakdown_analysis(current_user):
    return jsonify({"message": "Legacy breakdown analysis removed from raw-data schema"}), 410


@production_reports_bp.get("/reports/ytd-summary")
@login_required
def ytd_summary(current_user):
    year = int(request.args.get("year") or 0)
    month = int(request.args.get("month") or 0)
    if year <= 0 or month <= 0:
        return jsonify({"message": "year and month are required"}), 400
    return jsonify({"item": build_ytd_summary(year, month)})
