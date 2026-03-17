import os
import sys

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend import create_app
from backend.models import BreakdownReason, Machine, Plant
from backend.models.db import db


PLANTS = [
    {"code": "ACI", "name": "ACI / Suasa Plant"},
    {"code": "RS", "name": "RS / Keluli Plant"},
]

MACHINES = [
    {"plant_code": "ACI", "code": "530A", "name": "530A", "machine_group": "Group A", "display_order": 10},
    {"plant_code": "ACI", "code": "530B", "name": "530B", "machine_group": "Group A", "display_order": 20},
    {"plant_code": "ACI", "code": "570", "name": "570", "machine_group": "Group A", "display_order": 30},
    {"plant_code": "ACI", "code": "M8", "name": "M8", "machine_group": "Group A", "display_order": 40},
    {"plant_code": "ACI", "code": "MPL", "name": "MPL", "machine_group": "Group A", "display_order": 50},
    {"plant_code": "ACI", "code": "SPL", "name": "SPL", "machine_group": "Group A", "display_order": 60},
    {"plant_code": "RS", "code": "N530", "name": "N530", "machine_group": "Group B", "display_order": 70},
    {"plant_code": "RS", "code": "M16", "name": "M16", "machine_group": "Group B", "display_order": 80},
    {"plant_code": "RS", "code": "MANUAL_BAGGING", "name": "Manual bagging", "machine_group": "Group B", "display_order": 90},
]

BREAKDOWN_REASONS = [
    {"code": "ELECTRIC_PROBLEM", "name": "Electric problem", "display_order": 10},
    {"code": "CHANGE_RAW_MATERIAL", "name": "Change raw material", "display_order": 20},
    {"code": "CHANGE_DIE", "name": "Change die", "display_order": 30},
    {"code": "MACHINE_BREAKDOWN", "name": "Machine breakdown", "display_order": 40},
    {"code": "MANAGEMENT", "name": "Management", "display_order": 50},
    {"code": "EXTERNAL_FACTOR", "name": "External factor", "display_order": 60},
]


def seed():
    app = create_app("development")
    with app.app_context():
        plant_map = {}
        for payload in PLANTS:
            plant = Plant.query.filter_by(code=payload["code"]).first()
            if not plant:
                plant = Plant(**payload)
                db.session.add(plant)
                db.session.flush()
            plant_map[payload["code"]] = plant

        for payload in MACHINES:
            machine = Machine.query.filter_by(code=payload["code"]).first()
            if not machine:
                machine = Machine(
                    plant_id=plant_map[payload["plant_code"]].id,
                    code=payload["code"],
                    name=payload["name"],
                    machine_group=payload["machine_group"],
                    display_order=payload["display_order"],
                )
                db.session.add(machine)

        for payload in BREAKDOWN_REASONS:
            reason = BreakdownReason.query.filter_by(code=payload["code"]).first()
            if not reason:
                db.session.add(BreakdownReason(**payload))

        db.session.commit()
        print("Production module seed completed.")


if __name__ == "__main__":
    seed()
