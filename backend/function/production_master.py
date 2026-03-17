from flask import Blueprint, jsonify, request

from backend.function.common.decorators import login_required
from backend.models import Machine, Plant, Product
from backend.models.db import db
from backend.scripts.import_raw_excel_data import RAW_FILES, run_raw_data_import
from backend.models import (
    DailyMachinePlan,
    DailyProductTonnage,
    MonthlyEfficiencySummary,
    MonthlyMachineSummary,
    MonthlyProductTonnage,
)

production_master_bp = Blueprint("production_master", __name__)


def _bool_value(payload, key, default=True):
    value = payload.get(key, default)
    return bool(value)


def _machine_payload(machine):
    return {"item": machine.to_dict()}


def _product_payload(product):
    return {"item": product.to_dict()}


def _save_machine(machine, payload, is_create=False):
    plant_id = payload.get("plant_id", machine.plant_id if not is_create else None)
    code = (payload.get("code") or (machine.code if not is_create else "")).strip()
    name = (payload.get("name") or (machine.name if not is_create else "")).strip()

    if not plant_id or not code or not name:
        return None, (jsonify({"message": "plant_id, code and name are required"}), 400)

    duplicate_query = Machine.query.filter(Machine.code == code)
    if not is_create:
        duplicate_query = duplicate_query.filter(Machine.id != machine.id)
    duplicate = duplicate_query.first()
    if duplicate:
        return None, (jsonify({"message": "Machine code already exists"}), 409)

    machine.plant_id = plant_id
    machine.code = code
    machine.name = name
    machine.machine_group = (payload.get("machine_group") or machine.machine_group or "").strip() or None
    machine.display_order = int(payload.get("display_order", machine.display_order or 0))
    machine.is_active = _bool_value(payload, "is_active", machine.is_active if not is_create else True)
    machine.supports_output = _bool_value(payload, "supports_output", machine.supports_output if not is_create else True)
    machine.supports_reject = _bool_value(payload, "supports_reject", machine.supports_reject if not is_create else True)
    machine.supports_breakdown = _bool_value(payload, "supports_breakdown", machine.supports_breakdown if not is_create else True)
    machine.supports_efficiency = _bool_value(payload, "supports_efficiency", machine.supports_efficiency if not is_create else True)
    return machine, None


def _save_product(product, payload, is_create=False):
    part_code = (payload.get("part_code") or (product.part_code if not is_create else "")).strip()
    description = (payload.get("description") or (product.description if not is_create else "")).strip()

    if not part_code or not description:
        return None, (jsonify({"message": "part_code and description are required"}), 400)

    warehouse_code = (payload.get("warehouse_code") or product.warehouse_code or "").strip() or None
    duplicate_query = Product.query.filter(
        Product.part_code == part_code,
        Product.warehouse_code == warehouse_code,
    )
    if not is_create:
        duplicate_query = duplicate_query.filter(Product.id != product.id)
    duplicate = duplicate_query.first()
    if duplicate:
        return None, (jsonify({"message": "Product part_code + warehouse_code already exists"}), 409)

    product.plant_id = payload.get("plant_id", product.plant_id if not is_create else None)
    product.part_code = part_code
    product.description = description
    product.product_class = (payload.get("product_class") or product.product_class or "").strip() or None
    product.warehouse_code = warehouse_code
    product.is_active = _bool_value(payload, "is_active", product.is_active if not is_create else True)
    return product, None


@production_master_bp.get("/plants")
@login_required
def get_plants(current_user):
    plants = Plant.query.order_by(Plant.code.asc()).all()
    return jsonify({"items": [item.to_dict() for item in plants]})


@production_master_bp.get("/machines")
@login_required
def get_machines(current_user):
    machines = Machine.query.order_by(Machine.display_order.asc(), Machine.code.asc()).all()
    return jsonify({"items": [item.to_dict() for item in machines]})


@production_master_bp.post("/machines")
@login_required
def create_machine(current_user):
    payload = request.get_json(silent=True) or {}
    machine = Machine()
    machine, error_response = _save_machine(machine, payload, is_create=True)
    if error_response:
        return error_response
    db.session.add(machine)
    db.session.commit()
    return jsonify({"message": "Machine created", "item": machine.to_dict()}), 201


@production_master_bp.put("/machines/<int:machine_id>")
@login_required
def update_machine(machine_id, current_user):
    machine = Machine.query.get_or_404(machine_id)
    payload = request.get_json(silent=True) or {}
    machine, error_response = _save_machine(machine, payload, is_create=False)
    if error_response:
        return error_response
    db.session.commit()
    return jsonify({"message": "Machine updated", "item": machine.to_dict()})


@production_master_bp.get("/manage-machine")
@login_required
def manage_machine_list(current_user):
    machines = Machine.query.order_by(Machine.display_order.asc(), Machine.code.asc()).all()
    return jsonify({"items": [item.to_dict() for item in machines]})


@production_master_bp.post("/manage-machine")
@login_required
def manage_machine_create(current_user):
    payload = request.get_json(silent=True) or {}
    machine = Machine()
    machine, error_response = _save_machine(machine, payload, is_create=True)
    if error_response:
        return error_response
    db.session.add(machine)
    db.session.commit()
    return jsonify({"message": "Manage machine created", **_machine_payload(machine)}), 201


@production_master_bp.put("/manage-machine/<int:machine_id>")
@login_required
def manage_machine_update(machine_id, current_user):
    machine = Machine.query.get_or_404(machine_id)
    payload = request.get_json(silent=True) or {}
    machine, error_response = _save_machine(machine, payload, is_create=False)
    if error_response:
        return error_response
    db.session.commit()
    return jsonify({"message": "Manage machine updated", **_machine_payload(machine)})


@production_master_bp.get("/products")
@login_required
def get_products(current_user):
    products = Product.query.order_by(Product.part_code.asc()).all()
    return jsonify({"items": [item.to_dict() for item in products]})


@production_master_bp.post("/products")
@login_required
def create_product(current_user):
    payload = request.get_json(silent=True) or {}
    product = Product()
    product, error_response = _save_product(product, payload, is_create=True)
    if error_response:
        return error_response
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Product created", **_product_payload(product)}), 201


@production_master_bp.put("/products/<int:product_id>")
@login_required
def update_product(product_id, current_user):
    product = Product.query.get_or_404(product_id)
    payload = request.get_json(silent=True) or {}
    product, error_response = _save_product(product, payload, is_create=False)
    if error_response:
        return error_response
    db.session.commit()
    return jsonify({"message": "Product updated", **_product_payload(product)})


@production_master_bp.get("/breakdown-reasons")
@login_required
def get_breakdown_reasons(current_user):
    return jsonify({"message": "Legacy breakdown module removed from raw-data schema"}), 410


@production_master_bp.post("/breakdown-reasons")
@login_required
def create_breakdown_reason(current_user):
    return jsonify({"message": "Legacy breakdown module removed from raw-data schema"}), 410


@production_master_bp.put("/breakdown-reasons/<int:reason_id>")
@login_required
def update_breakdown_reason(reason_id, current_user):
    return jsonify({"message": "Legacy breakdown module removed from raw-data schema"}), 410


@production_master_bp.get("/annual-targets")
@login_required
def get_annual_targets(current_user):
    return jsonify({"message": "Legacy annual target module removed; use daily_machine_plan and monthly_efficiency_summary"}), 410


@production_master_bp.post("/annual-targets")
@login_required
def create_annual_target(current_user):
    return jsonify({"message": "Legacy annual target module removed; use daily_machine_plan and monthly_efficiency_summary"}), 410


@production_master_bp.put("/annual-targets/<int:target_id>")
@login_required
def update_annual_target(target_id, current_user):
    return jsonify({"message": "Legacy annual target module removed; use daily_machine_plan and monthly_efficiency_summary"}), 410


@production_master_bp.get("/raw-data/summary")
@login_required
def get_raw_data_summary(current_user):
    return jsonify(
        {
            "files": {name: str(path) for name, path in RAW_FILES.items()},
            "counts": {
                "plants": Plant.query.count(),
                "machines": Machine.query.count(),
                "products": Product.query.count(),
                "daily_product_tonnage_rows": DailyProductTonnage.query.count(),
                "monthly_product_tonnage_rows": MonthlyProductTonnage.query.count(),
                "daily_machine_plan_rows": DailyMachinePlan.query.count(),
                "monthly_machine_summary_rows": MonthlyMachineSummary.query.count(),
                "monthly_efficiency_summary_rows": MonthlyEfficiencySummary.query.count(),
            },
        }
    )


@production_master_bp.post("/raw-data/import")
@login_required
def import_raw_data(current_user):
    if not current_user.is_admin:
        return jsonify({"message": "Admin access required"}), 403

    summary = run_raw_data_import()
    return jsonify({"message": "Raw data import completed", "summary": summary})
