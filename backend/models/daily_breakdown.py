from datetime import datetime

from backend.models.db import db


class DailyBreakdownRecord(db.Model):
    __tablename__ = "daily_breakdown_record"

    id = db.Column(db.Integer, primary_key=True)
    record_date = db.Column(db.Date, nullable=False, index=True)
    machine_id = db.Column(db.Integer, db.ForeignKey("machine.id"), nullable=False, index=True)
    breakdown_reason_id = db.Column(
        db.Integer,
        db.ForeignKey("breakdown_reason.id"),
        nullable=False,
        index=True,
    )
    downtime_hours = db.Column(db.Numeric(8, 2), nullable=False)
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
    breakdown_reason = db.relationship("BreakdownReason", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "machine_id": self.machine_id,
            "breakdown_reason_id": self.breakdown_reason_id,
            "downtime_hours": float(self.downtime_hours or 0),
            "remarks": self.remarks,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "machine": self.machine.to_dict() if self.machine else None,
            "breakdown_reason": self.breakdown_reason.to_dict() if self.breakdown_reason else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
