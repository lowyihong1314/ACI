from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import extract

from backend.models import (
    DailyMachinePlan,
    DailyProductTonnage,
    Machine,
    MonthlyEfficiencySummary,
    MonthlyMachineSummary,
)


def parse_iso_date(value: str | None) -> date:
    if not value:
        raise ValueError("date is required")
    return datetime.strptime(value, "%Y-%m-%d").date()


def parse_year_month(value: str | None) -> tuple[int, int]:
    if not value:
        raise ValueError("month is required")
    parsed = datetime.strptime(value, "%Y-%m")
    return parsed.year, parsed.month


def safe_float(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def efficiency_percentage(numerator: float, denominator: float):
    if denominator <= 0:
        return None
    return (numerator / denominator) * 100


def get_month_product_tonnage_records(year: int, month: int):
    return (
        DailyProductTonnage.query
        .filter(
            extract("year", DailyProductTonnage.record_date) == year,
            extract("month", DailyProductTonnage.record_date) == month,
        )
        .order_by(DailyProductTonnage.record_date.asc(), DailyProductTonnage.product_id.asc())
        .all()
    )


def get_month_machine_plan_records(year: int, month: int):
    return (
        DailyMachinePlan.query.join(Machine)
        .filter(
            extract("year", DailyMachinePlan.plan_date) == year,
            extract("month", DailyMachinePlan.plan_date) == month,
        )
        .order_by(Machine.display_order.asc(), DailyMachinePlan.plan_date.asc())
        .all()
    )


def build_monthly_machine_summary(year: int, month: int):
    summary_records = (
        MonthlyMachineSummary.query.join(Machine)
        .filter(
            extract("year", MonthlyMachineSummary.month_start) == year,
            extract("month", MonthlyMachineSummary.month_start) == month,
        )
        .order_by(Machine.display_order.asc(), Machine.code.asc())
        .all()
    )
    plan_records = get_month_machine_plan_records(year, month)
    plan_totals = defaultdict(float)
    for item in plan_records:
        plan_totals[item.machine_id] += safe_float(item.planned_output_mt)

    grouped = {}
    for item in summary_records:
        machine = item.machine
        bucket = grouped.setdefault(
            machine.id,
            {
                "machine_id": machine.id,
                "machine_code": machine.code,
                "machine_name": machine.name,
                "machine_group": machine.machine_group,
                "plant_id": machine.plant.id if machine.plant else None,
                "plant_code": machine.plant.code if machine.plant else None,
                "plant_name": machine.plant.name if machine.plant else None,
                "actual_output_mt": 0.0,
                "planned_output_mt": 0.0,
                "rejected_output_mt": 0.0,
            },
        )
        bucket["actual_output_mt"] = safe_float(item.actual_output_mt)
        bucket["rejected_output_mt"] = safe_float(item.rejected_output_mt)
        bucket["planned_output_mt"] = plan_totals.get(machine.id, 0.0)

    for bucket in grouped.values():
        bucket["plan_attainment_pct"] = efficiency_percentage(
            bucket["actual_output_mt"],
            bucket["planned_output_mt"],
        )

    return list(grouped.values())


def build_monthly_plant_summary(year: int, month: int):
    machine_summary = build_monthly_machine_summary(year, month)
    grouped = {}

    for item in machine_summary:
        bucket = grouped.setdefault(
            item["plant_id"],
            {
                "plant_id": item["plant_id"],
                "plant_code": item["plant_code"],
                "plant_name": item["plant_name"],
                "actual_output_mt": 0.0,
                "planned_output_mt": 0.0,
                "rejected_output_mt": 0.0,
            },
        )
        bucket["actual_output_mt"] += item["actual_output_mt"]
        bucket["planned_output_mt"] += item["planned_output_mt"]
        bucket["rejected_output_mt"] += item["rejected_output_mt"]

    for bucket in grouped.values():
        bucket["plan_attainment_pct"] = efficiency_percentage(
            bucket["actual_output_mt"],
            bucket["planned_output_mt"],
        )

    return list(grouped.values())


def build_breakdown_analysis(year: int, month: int):
    return []


def build_ytd_summary(year: int, month: int):
    overall_records = (
        MonthlyEfficiencySummary.query
        .filter(
            MonthlyEfficiencySummary.scope_code == "OVERALL",
            extract("year", MonthlyEfficiencySummary.month_start) == year,
            extract("month", MonthlyEfficiencySummary.month_start) <= month,
        )
        .all()
    )

    if overall_records:
        actual_total = sum(safe_float(item.actual_output_mt) for item in overall_records)
        planned_total = sum(safe_float(item.planned_output_mt) for item in overall_records)
        return {
            "year": year,
            "through_month": month,
            "actual_output_mt": actual_total,
            "planned_output_mt": planned_total,
            "output_efficiency_pct": efficiency_percentage(actual_total, planned_total),
        }

    machine_records = (
        MonthlyMachineSummary.query
        .filter(
            extract("year", MonthlyMachineSummary.month_start) == year,
            extract("month", MonthlyMachineSummary.month_start) <= month,
        )
        .all()
    )
    plan_records = (
        DailyMachinePlan.query
        .filter(
            extract("year", DailyMachinePlan.plan_date) == year,
            extract("month", DailyMachinePlan.plan_date) <= month,
        )
        .all()
    )

    actual_total = sum(safe_float(item.actual_output_mt) for item in machine_records)
    planned_total = sum(safe_float(item.planned_output_mt) for item in plan_records)
    rejected_total = sum(safe_float(item.rejected_output_mt) for item in machine_records)

    return {
        "year": year,
        "through_month": month,
        "actual_output_mt": actual_total,
        "planned_output_mt": planned_total,
        "rejected_output_mt": rejected_total,
        "output_efficiency_pct": efficiency_percentage(actual_total, planned_total),
    }
