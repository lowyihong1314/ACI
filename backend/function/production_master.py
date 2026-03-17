from flask import Blueprint, jsonify, request

from backend.function.common.decorators import login_required
from backend.services.production_service import (
    ProductionServiceError,
    create_machine,
    create_plant,
    create_product,
    delete_machine,
    delete_plant,
    delete_product,
    list_machines,
    list_plants,
    list_products,
    update_machine,
    update_plant,
    update_product,
)

production_master_bp = Blueprint("production_master", __name__)


def _service_response(action, success_message, success_status=200):
    try:
        item = action()
        payload = {"message": success_message}
        if item is not None:
            payload["item"] = item.to_dict()
        return jsonify(payload), success_status
    except ProductionServiceError as exc:
        return jsonify({"message": exc.message}), exc.status_code


@production_master_bp.get("/plants")
@login_required
def get_plants(current_user):
    return jsonify({"items": [item.to_dict() for item in list_plants()]})


@production_master_bp.post("/plants")
@login_required
def post_plant(current_user):
    payload = request.get_json(silent=True) or {}
    return _service_response(lambda: create_plant(payload), "Plant created", 201)


@production_master_bp.put("/plants/<int:plant_id>")
@login_required
def put_plant(plant_id, current_user):
    payload = request.get_json(silent=True) or {}
    return _service_response(lambda: update_plant(plant_id, payload), "Plant updated")


@production_master_bp.delete("/plants/<int:plant_id>")
@login_required
def remove_plant(plant_id, current_user):
    return _service_response(lambda: delete_plant(plant_id), "Plant deleted")


@production_master_bp.get("/machines")
@login_required
def get_machines(current_user):
    return jsonify({"items": [item.to_dict() for item in list_machines()]})


@production_master_bp.post("/machines")
@login_required
def post_machine(current_user):
    payload = request.get_json(silent=True) or {}
    return _service_response(lambda: create_machine(payload), "Machine created", 201)


@production_master_bp.put("/machines/<int:machine_id>")
@login_required
def put_machine(machine_id, current_user):
    payload = request.get_json(silent=True) or {}
    return _service_response(lambda: update_machine(machine_id, payload), "Machine updated")


@production_master_bp.delete("/machines/<int:machine_id>")
@login_required
def remove_machine(machine_id, current_user):
    return _service_response(lambda: delete_machine(machine_id), "Machine deleted")


@production_master_bp.get("/manage-machine")
@login_required
def manage_machine_list(current_user):
    return jsonify({"items": [item.to_dict() for item in list_machines()]})


@production_master_bp.post("/manage-machine")
@login_required
def manage_machine_create(current_user):
    payload = request.get_json(silent=True) or {}
    return _service_response(lambda: create_machine(payload), "Manage machine created", 201)


@production_master_bp.put("/manage-machine/<int:machine_id>")
@login_required
def manage_machine_update(machine_id, current_user):
    payload = request.get_json(silent=True) or {}
    return _service_response(lambda: update_machine(machine_id, payload), "Manage machine updated")


@production_master_bp.delete("/manage-machine/<int:machine_id>")
@login_required
def manage_machine_delete(machine_id, current_user):
    return _service_response(lambda: delete_machine(machine_id), "Manage machine deleted")


@production_master_bp.get("/products")
@login_required
def get_products(current_user):
    return jsonify({"items": [item.to_dict() for item in list_products()]})


@production_master_bp.post("/products")
@login_required
def post_product(current_user):
    payload = request.get_json(silent=True) or {}
    return _service_response(lambda: create_product(payload), "Product created", 201)


@production_master_bp.put("/products/<int:product_id>")
@login_required
def put_product(product_id, current_user):
    payload = request.get_json(silent=True) or {}
    return _service_response(lambda: update_product(product_id, payload), "Product updated")


@production_master_bp.delete("/products/<int:product_id>")
@login_required
def remove_product(product_id, current_user):
    return _service_response(lambda: delete_product(product_id), "Product deleted")


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
    return jsonify({"message": "Raw data import module disabled; maintain records from the frontend forms."}), 410


@production_master_bp.post("/raw-data/import")
@login_required
def import_raw_data(current_user):
    return jsonify({"message": "Raw data import module disabled; maintain records from the frontend forms."}), 410
