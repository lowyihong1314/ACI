from datetime import datetime

from backend.models.db import db


class DailyProductionRecord(db.Model):
    __tablename__ = "daily_production_record"
    __table_args__ = (
        db.UniqueConstraint("record_date", "machine_id", name="uq_daily_production_record"),
    )

    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.Date, nullable=False, index=True)
    machine_id = db.Column(db.Integer, db.ForeignKey("machine.id"), nullable=False, index=True)
    actual_output_mt = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    target_output_mt = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    reject_qty_mt = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    available_hours = db.Column(db.Numeric(8, 2), nullable=False, default=0)
    remarks = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("user_data.id"), nullable=False)
    updated_by = db.Column(db.Integer, db.ForeignKey("user_data.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    machine = db.relationship("Machine", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "machine_id": self.machine_id,
            "actual_output_mt": float(self.actual_output_mt or 0),
            "target_output_mt": float(self.target_output_mt or 0),
            "reject_qty_mt": float(self.reject_qty_mt or 0),
            "available_hours": float(self.available_hours or 0),
            "remarks": self.remarks,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "machine": self.machine.to_dict() if self.machine else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
