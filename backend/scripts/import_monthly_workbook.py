import os
import sys
from calendar import monthrange
from datetime import date

from openpyxl import load_workbook

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
BACKEND_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend import create_app
from backend.models import (
    AnnualMachineTarget,
    BreakdownReason,
    DailyBreakdownRecord,
    DailyProductionRecord,
    Machine,
    UserData,
)
from backend.models.db import db


MONTH_ROW_MAP = {
    "Jan": 3,
    "Feb": 4,
}

PRODUCTION_COLUMN_MAP = {
    "530A": {"actual": "B", "target": "C", "reject": "H"},
    "530B": {"actual": "G", "target": "H", "reject": "I"},
    "570": {"actual": "L", "target": "M", "reject": "J"},
    "M8": {"actual": "Q", "target": "R", "reject": "K"},
    "MPL": {"actual": "V", "target": "W", "reject": "L"},
    "SPL": {"actual": "AA", "target": "AB", "reject": "M"},
    "N530": {"actual": "AF", "target": "AG", "reject": "N"},
    "M16": {"actual": "AK", "target": "AL", "reject": "O"},
    "MANUAL_BAGGING": {"actual": "AP", "target": "AQ", "reject": "P"},
}

ACI_AVAILABLE_HOURS = {
    "Jan": {"530A": "D", "530B": "E", "570": "F", "M8": "G", "MPL": "H", "SPL": "I"},
    "Feb": {"530A": "J", "530B": "K", "570": "L", "M8": "M", "MPL": "N", "SPL": "O"},
}

RS_AVAILABLE_HOURS = {
    "Jan": {"M16": "D", "N530": "E"},
    "Feb": {"M16": "F", "N530": "G"},
}

ACI_BREAKDOWN_COLUMNS = {
    "Jan": {"530A": "D", "530B": "E", "570": "F", "M8": "G", "MPL": "H", "SPL": "I"},
    "Feb": {"530A": "J", "530B": "K", "570": "L", "M8": "M", "MPL": "N", "SPL": "O"},
}

RS_BREAKDOWN_COLUMNS = {
    "Jan": {"M16": "D", "N530": "E"},
    "Feb": {"M16": "F", "N530": "G"},
}

BREAKDOWN_ROW_MAP = {
    38: "ELECTRIC_PROBLEM",
    39: "CHANGE_RAW_MATERIAL",
    40: "CHANGE_DIE",
    41: "MACHINE_BREAKDOWN",
    42: "MANAGEMENT",
    43: "EXTERNAL_FACTOR",
    50: "ELECTRIC_PROBLEM",
    51: "CHANGE_RAW_MATERIAL",
    52: "CHANGE_DIE",
    53: "MACHINE_BREAKDOWN",
    54: "MANAGEMENT",
    55: "EXTERNAL_FACTOR",
}

ANNUAL_TARGET_ROW_MAP = {
    "530A": 6,
    "530B": 7,
    "570": 8,
    "M8": 9,
    "MPL": 10,
    "SPL": 11,
    "N530": 13,
    "M16": 14,
    "MANUAL_BAGGING": 15,
}


def numeric(value):
    if value in (None, ""):
        return 0.0
    return float(value)


def month_end(year: int, month: int) -> date:
    return date(year, month, monthrange(year, month)[1])


def import_workbook(path: str):
    app = create_app("development")
    workbook = load_workbook(path, data_only=True)
    data_sheet = workbook["DATA"]
    jan_sheet = workbook["JAN26"]

    with app.app_context():
        admin = UserData.query.filter_by(username="admin").first()
        if not admin:
            raise RuntimeError("Admin user not found. Expected default admin to exist.")

        machine_map = {item.code: item for item in Machine.query.all()}
        reason_map = {item.code: item for item in BreakdownReason.query.all()}

        for machine_code, source_row in ANNUAL_TARGET_ROW_MAP.items():
            machine = machine_map.get(machine_code)
            if not machine:
                continue
            annual_target = numeric(jan_sheet[f"O{source_row}"].value or workbook["FEB26"][f"O{source_row}"].value)
            target = AnnualMachineTarget.query.filter_by(year=2026, machine_id=machine.id).first()
            if not target:
                target = AnnualMachineTarget(year=2026, machine_id=machine.id)
                db.session.add(target)
            target.annual_target_mt = annual_target

        for month_name, row_number in MONTH_ROW_MAP.items():
            record_date = month_end(2026, 1 if month_name == "Jan" else 2)

            for machine_code, columns in PRODUCTION_COLUMN_MAP.items():
                machine = machine_map.get(machine_code)
                if not machine:
                    continue

                available_hours = 0.0
                if machine_code in ACI_AVAILABLE_HOURS.get(month_name, {}):
                    available_hours = numeric(data_sheet[f"{ACI_AVAILABLE_HOURS[month_name][machine_code]}45"].value)
                if machine_code in RS_AVAILABLE_HOURS.get(month_name, {}):
                    available_hours = numeric(data_sheet[f"{RS_AVAILABLE_HOURS[month_name][machine_code]}57"].value)

                record = DailyProductionRecord.query.filter_by(
                    record_date=record_date,
                    machine_id=machine.id,
                ).first()
                if not record:
                    record = DailyProductionRecord(
                        record_date=record_date,
                        machine_id=machine.id,
                        created_by=admin.id,
                        updated_by=admin.id,
                    )
                    db.session.add(record)

                record.actual_output_mt = numeric(data_sheet[f"{columns['actual']}{row_number}"].value)
                record.target_output_mt = numeric(data_sheet[f"{columns['target']}{row_number}"].value)
                record.reject_qty_mt = numeric(data_sheet[f"{columns['reject']}20"].value if month_name == "Jan" else data_sheet[f"{columns['reject']}21"].value)
                record.available_hours = available_hours
                record.remarks = (
                    f"Imported from workbook month-end snapshot: {os.path.basename(path)} ({month_name} 2026). "
                    "Source file contains monthly summary, not true daily source."
                )
                record.updated_by = admin.id

            for machine_code, column in ACI_BREAKDOWN_COLUMNS.get(month_name, {}).items():
                machine = machine_map.get(machine_code)
                if not machine:
                    continue
                for row_index in range(38, 44):
                    hours = numeric(data_sheet[f"{column}{row_index}"].value)
                    if hours <= 0:
                        continue
                    reason = reason_map[BREAKDOWN_ROW_MAP[row_index]]
                    item = DailyBreakdownRecord.query.filter_by(
                        record_date=record_date,
                        machine_id=machine.id,
                        breakdown_reason_id=reason.id,
                    ).first()
                    if not item:
                        item = DailyBreakdownRecord(
                            record_date=record_date,
                            machine_id=machine.id,
                            breakdown_reason_id=reason.id,
                            created_by=admin.id,
                            updated_by=admin.id,
                        )
                        db.session.add(item)
                    item.downtime_hours = hours
                    item.remarks = (
                        f"Imported from workbook month-end snapshot: {os.path.basename(path)} ({month_name} 2026)."
                    )
                    item.updated_by = admin.id

            for machine_code, column in RS_BREAKDOWN_COLUMNS.get(month_name, {}).items():
                machine = machine_map.get(machine_code)
                if not machine:
                    continue
                for row_index in range(50, 56):
                    hours = numeric(data_sheet[f"{column}{row_index}"].value)
                    if hours <= 0:
                        continue
                    reason = reason_map[BREAKDOWN_ROW_MAP[row_index]]
                    item = DailyBreakdownRecord.query.filter_by(
                        record_date=record_date,
                        machine_id=machine.id,
                        breakdown_reason_id=reason.id,
                    ).first()
                    if not item:
                        item = DailyBreakdownRecord(
                            record_date=record_date,
                            machine_id=machine.id,
                            breakdown_reason_id=reason.id,
                            created_by=admin.id,
                            updated_by=admin.id,
                        )
                        db.session.add(item)
                    item.downtime_hours = hours
                    item.remarks = (
                        f"Imported from workbook month-end snapshot: {os.path.basename(path)} ({month_name} 2026)."
                    )
                    item.updated_by = admin.id

        db.session.commit()
        print("Workbook import completed.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python scripts/import_monthly_workbook.py <xlsx_path>")
    import_workbook(os.path.abspath(sys.argv[1]))
