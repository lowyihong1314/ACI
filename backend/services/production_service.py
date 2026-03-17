from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import extract

from backend.models import (
    DailyMachinePlan,
    DailyProductTonnage,
    MonthlyProductTonnage,
    Machine,
    MonthlyEfficiencySummary,
    MonthlyMachineSummary,
    Plant,
    Product,
)
from backend.models.db import db


class ProductionServiceError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


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


def _normalize_text(value):
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _require_positive_int(value, field_name: str) -> int:
    try:
        parsed = int(value or 0)
    except (TypeError, ValueError) as exc:
        raise ProductionServiceError(f"{field_name} must be an integer") from exc
    if parsed <= 0:
        raise ProductionServiceError(f"{field_name} is required")
    return parsed


def _parse_optional_positive_int(value, field_name: str):
    if value in (None, ""):
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ProductionServiceError(f"{field_name} must be an integer") from exc
    if parsed <= 0:
        raise ProductionServiceError(f"{field_name} must be greater than 0")
    return parsed


def _parse_non_negative_float(value, field_name: str, *, required=False, allow_null=False):
    if value in (None, ""):
        if allow_null:
            return None
        if required:
            raise ProductionServiceError(f"{field_name} is required")
        return 0.0
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ProductionServiceError(f"{field_name} must be a number") from exc
    if parsed < 0:
        raise ProductionServiceError(f"{field_name} must be >= 0")
    return parsed


def _bool_value(payload, key, default=True):
    value = payload.get(key, default)
    return bool(value)


def _get_plant_or_error(plant_id: int) -> Plant:
    plant = Plant.query.get(plant_id)
    if not plant:
        raise ProductionServiceError("Plant not found", 404)
    return plant


def _get_machine_or_error(machine_id: int) -> Machine:
    machine = Machine.query.get(machine_id)
    if not machine:
        raise ProductionServiceError("Machine not found", 404)
    return machine


def _get_product_or_error(product_id: int) -> Product:
    product = Product.query.get(product_id)
    if not product:
        raise ProductionServiceError("Product not found", 404)
    return product


def _get_daily_product_tonnage_or_error(record_id: int) -> DailyProductTonnage:
    record = DailyProductTonnage.query.get(record_id)
    if not record:
        raise ProductionServiceError("Daily production record not found", 404)
    return record


def _get_daily_machine_plan_or_error(record_id: int) -> DailyMachinePlan:
    record = DailyMachinePlan.query.get(record_id)
    if not record:
        raise ProductionServiceError("Daily machine plan not found", 404)
    return record


def list_plants():
    return Plant.query.order_by(Plant.code.asc()).all()


def create_plant(payload):
    plant = Plant()
    plant.name = _normalize_text(payload.get("name"))
    plant.code = _normalize_text(payload.get("code"))
    plant.is_active = _bool_value(payload, "is_active", True)

    if not plant.name or not plant.code:
        raise ProductionServiceError("name and code are required")

    duplicate = Plant.query.filter(Plant.code == plant.code).first()
    if duplicate:
        raise ProductionServiceError("Plant code already exists", 409)

    db.session.add(plant)
    db.session.commit()
    return plant


def update_plant(plant_id: int, payload):
    plant = _get_plant_or_error(plant_id)

    next_name = _normalize_text(payload.get("name", plant.name))
    next_code = _normalize_text(payload.get("code", plant.code))
    if not next_name or not next_code:
        raise ProductionServiceError("name and code are required")

    duplicate = Plant.query.filter(Plant.code == next_code, Plant.id != plant.id).first()
    if duplicate:
        raise ProductionServiceError("Plant code already exists", 409)

    plant.name = next_name
    plant.code = next_code
    plant.is_active = _bool_value(payload, "is_active", plant.is_active)
    db.session.commit()
    return plant


def delete_plant(plant_id: int):
    plant = _get_plant_or_error(plant_id)
    if Machine.query.filter(Machine.plant_id == plant.id).first():
        raise ProductionServiceError("Cannot delete plant with existing machines", 409)
    if Product.query.filter(Product.plant_id == plant.id).first():
        raise ProductionServiceError("Cannot delete plant with existing products", 409)
    db.session.delete(plant)
    db.session.commit()


def list_machines():
    return Machine.query.order_by(Machine.display_order.asc(), Machine.code.asc()).all()


def create_machine(payload):
    plant_id = _require_positive_int(payload.get("plant_id"), "plant_id")
    _get_plant_or_error(plant_id)
    code = _normalize_text(payload.get("code"))
    name = _normalize_text(payload.get("name"))
    if not code or not name:
        raise ProductionServiceError("plant_id, code and name are required")
    duplicate = Machine.query.filter(Machine.code == code).first()
    if duplicate:
        raise ProductionServiceError("Machine code already exists", 409)

    machine = Machine(
        plant_id=plant_id,
        code=code,
        name=name,
        machine_group=_normalize_text(payload.get("machine_group")),
        display_order=int(payload.get("display_order") or 0),
        is_active=_bool_value(payload, "is_active", True),
        supports_output=_bool_value(payload, "supports_output", True),
        supports_reject=_bool_value(payload, "supports_reject", True),
        supports_breakdown=_bool_value(payload, "supports_breakdown", True),
        supports_efficiency=_bool_value(payload, "supports_efficiency", True),
    )
    db.session.add(machine)
    db.session.commit()
    return machine


def update_machine(machine_id: int, payload):
    machine = _get_machine_or_error(machine_id)
    plant_id = _require_positive_int(payload.get("plant_id", machine.plant_id), "plant_id")
    _get_plant_or_error(plant_id)
    code = _normalize_text(payload.get("code", machine.code))
    name = _normalize_text(payload.get("name", machine.name))
    if not code or not name:
        raise ProductionServiceError("plant_id, code and name are required")

    duplicate = Machine.query.filter(Machine.code == code, Machine.id != machine.id).first()
    if duplicate:
        raise ProductionServiceError("Machine code already exists", 409)

    machine.plant_id = plant_id
    machine.code = code
    machine.name = name
    machine.machine_group = _normalize_text(payload.get("machine_group", machine.machine_group))
    machine.display_order = int(payload.get("display_order", machine.display_order or 0))
    machine.is_active = _bool_value(payload, "is_active", machine.is_active)
    machine.supports_output = _bool_value(payload, "supports_output", machine.supports_output)
    machine.supports_reject = _bool_value(payload, "supports_reject", machine.supports_reject)
    machine.supports_breakdown = _bool_value(payload, "supports_breakdown", machine.supports_breakdown)
    machine.supports_efficiency = _bool_value(payload, "supports_efficiency", machine.supports_efficiency)
    db.session.commit()
    return machine


def delete_machine(machine_id: int):
    machine = _get_machine_or_error(machine_id)
    if DailyMachinePlan.query.filter(DailyMachinePlan.machine_id == machine.id).first():
        raise ProductionServiceError("Cannot delete machine with existing daily plans", 409)
    if MonthlyMachineSummary.query.filter(MonthlyMachineSummary.machine_id == machine.id).first():
        raise ProductionServiceError("Cannot delete machine with existing monthly summary data", 409)
    db.session.delete(machine)
    db.session.commit()


def list_products():
    return Product.query.order_by(Product.part_code.asc()).all()


def create_product(payload):
    part_code = _normalize_text(payload.get("part_code"))
    description = _normalize_text(payload.get("description"))
    if not part_code or not description:
        raise ProductionServiceError("part_code and description are required")

    warehouse_code = _normalize_text(payload.get("warehouse_code"))
    plant_id = _parse_optional_positive_int(payload.get("plant_id"), "plant_id")
    if plant_id is not None:
        _get_plant_or_error(plant_id)

    duplicate = Product.query.filter(
        Product.part_code == part_code,
        Product.warehouse_code == warehouse_code,
    ).first()
    if duplicate:
        raise ProductionServiceError("Product part_code + warehouse_code already exists", 409)

    product = Product(
        plant_id=plant_id,
        part_code=part_code,
        description=description,
        product_class=_normalize_text(payload.get("product_class")),
        warehouse_code=warehouse_code,
        is_active=_bool_value(payload, "is_active", True),
    )
    db.session.add(product)
    db.session.commit()
    return product


def update_product(product_id: int, payload):
    product = _get_product_or_error(product_id)
    part_code = _normalize_text(payload.get("part_code", product.part_code))
    description = _normalize_text(payload.get("description", product.description))
    if not part_code or not description:
        raise ProductionServiceError("part_code and description are required")

    warehouse_code = _normalize_text(payload.get("warehouse_code", product.warehouse_code))
    plant_id = _parse_optional_positive_int(payload.get("plant_id", product.plant_id), "plant_id")
    if plant_id is not None:
        _get_plant_or_error(plant_id)

    duplicate = Product.query.filter(
        Product.part_code == part_code,
        Product.warehouse_code == warehouse_code,
        Product.id != product.id,
    ).first()
    if duplicate:
        raise ProductionServiceError("Product part_code + warehouse_code already exists", 409)

    product.plant_id = plant_id
    product.part_code = part_code
    product.description = description
    product.product_class = _normalize_text(payload.get("product_class", product.product_class))
    product.warehouse_code = warehouse_code
    product.is_active = _bool_value(payload, "is_active", product.is_active)
    db.session.commit()
    return product


def delete_product(product_id: int):
    product = _get_product_or_error(product_id)
    if DailyProductTonnage.query.filter(DailyProductTonnage.product_id == product.id).first():
        raise ProductionServiceError("Cannot delete product with existing daily output records", 409)
    if MonthlyProductTonnage.query.filter(MonthlyProductTonnage.product_id == product.id).first():
        raise ProductionServiceError("Cannot delete product with existing monthly output data", 409)
    db.session.delete(product)
    db.session.commit()


def create_daily_product_tonnage(payload):
    record_date = parse_iso_date(payload.get("record_date"))
    product_id = _require_positive_int(payload.get("product_id"), "product_id")
    _get_product_or_error(product_id)
    output_mt = _parse_non_negative_float(payload.get("output_mt"), "output_mt")

    duplicate = DailyProductTonnage.query.filter_by(
        record_date=record_date,
        product_id=product_id,
    ).first()
    if duplicate:
        raise ProductionServiceError("Daily production record already exists for this product and date", 409)

    record = DailyProductTonnage(
        record_date=record_date,
        product_id=product_id,
        output_mt=output_mt,
    )
    db.session.add(record)
    db.session.commit()
    return record


def update_daily_product_tonnage(record_id: int, payload):
    record = _get_daily_product_tonnage_or_error(record_id)
    record_date = parse_iso_date(payload.get("record_date") or record.record_date.isoformat())
    product_id = _require_positive_int(payload.get("product_id", record.product_id), "product_id")
    _get_product_or_error(product_id)
    output_mt = _parse_non_negative_float(payload.get("output_mt", record.output_mt), "output_mt")

    duplicate = DailyProductTonnage.query.filter(
        DailyProductTonnage.record_date == record_date,
        DailyProductTonnage.product_id == product_id,
        DailyProductTonnage.id != record.id,
    ).first()
    if duplicate:
        raise ProductionServiceError("Daily production record already exists for this product and date", 409)

    record.record_date = record_date
    record.product_id = product_id
    record.output_mt = output_mt
    db.session.commit()
    return record


def delete_daily_product_tonnage(record_id: int):
    record = _get_daily_product_tonnage_or_error(record_id)
    db.session.delete(record)
    db.session.commit()


def create_daily_machine_plan(payload):
    plan_date = parse_iso_date(payload.get("plan_date"))
    machine_id = _require_positive_int(payload.get("machine_id"), "machine_id")
    _get_machine_or_error(machine_id)
    planned_output_mt = _parse_non_negative_float(payload.get("planned_output_mt"), "planned_output_mt")
    standard_output_mt = _parse_non_negative_float(
        payload.get("standard_output_mt"),
        "standard_output_mt",
        allow_null=True,
    )

    duplicate = DailyMachinePlan.query.filter_by(plan_date=plan_date, machine_id=machine_id).first()
    if duplicate:
        raise ProductionServiceError("Daily machine plan already exists for this machine and date", 409)

    record = DailyMachinePlan(
        plan_date=plan_date,
        machine_id=machine_id,
        planned_output_mt=planned_output_mt,
        standard_output_mt=standard_output_mt,
    )
    db.session.add(record)
    db.session.commit()
    return record


def update_daily_machine_plan(record_id: int, payload):
    record = _get_daily_machine_plan_or_error(record_id)
    plan_date = parse_iso_date(payload.get("plan_date") or record.plan_date.isoformat())
    machine_id = _require_positive_int(payload.get("machine_id", record.machine_id), "machine_id")
    _get_machine_or_error(machine_id)
    planned_output_mt = _parse_non_negative_float(
        payload.get("planned_output_mt", record.planned_output_mt),
        "planned_output_mt",
    )
    standard_output_mt = _parse_non_negative_float(
        payload.get("standard_output_mt", record.standard_output_mt),
        "standard_output_mt",
        allow_null=True,
    )

    duplicate = DailyMachinePlan.query.filter(
        DailyMachinePlan.plan_date == plan_date,
        DailyMachinePlan.machine_id == machine_id,
        DailyMachinePlan.id != record.id,
    ).first()
    if duplicate:
        raise ProductionServiceError("Daily machine plan already exists for this machine and date", 409)

    record.plan_date = plan_date
    record.machine_id = machine_id
    record.planned_output_mt = planned_output_mt
    record.standard_output_mt = standard_output_mt
    db.session.commit()
    return record


def delete_daily_machine_plan(record_id: int):
    record = _get_daily_machine_plan_or_error(record_id)
    db.session.delete(record)
    db.session.commit()


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


def build_daily_plan_vs_actual(end_date: date, days: int = 7, machine_id: int | None = None):
    if days <= 0:
        raise ValueError("days must be greater than 0")

    start_date = end_date - timedelta(days=days - 1)

    actual_rows = (
        DailyProductTonnage.query
        .filter(
            DailyProductTonnage.record_date >= start_date,
            DailyProductTonnage.record_date <= end_date,
        )
        .all()
    )
    plan_rows = (
        DailyMachinePlan.query
        .filter(
            DailyMachinePlan.plan_date >= start_date,
            DailyMachinePlan.plan_date <= end_date,
        )
        .filter(DailyMachinePlan.machine_id == machine_id if machine_id else True)
        .all()
    )

    actual_by_date = defaultdict(float)
    for row in actual_rows:
        actual_by_date[row.record_date] += safe_float(row.output_mt)

    plan_by_date = defaultdict(float)
    for row in plan_rows:
        plan_by_date[row.plan_date] += safe_float(row.planned_output_mt)

    items = []
    for index in range(days):
        current_date = start_date + timedelta(days=index)
        actual_output_mt = actual_by_date.get(current_date, 0.0)
        planned_output_mt = plan_by_date.get(current_date, 0.0)
        items.append({
            "date": current_date.isoformat(),
            "actual_output_mt": actual_output_mt,
            "planned_output_mt": planned_output_mt,
            "plan_attainment_pct": efficiency_percentage(actual_output_mt, planned_output_mt),
        })

    return items
