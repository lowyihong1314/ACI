from datetime import datetime

from backend.models.db import db


class MonthlyMachineSummary(db.Model):
    __tablename__ = "monthly_machine_summary"
    __table_args__ = (
        db.UniqueConstraint("month_start", "machine_id", name="uq_monthly_machine_summary"),
    )

    id = db.Column(db.Integer, primary_key=True)
    month_start = db.Column(db.Date, nullable=False, index=True)
    machine_id = db.Column(db.Integer, db.ForeignKey("machine.id"), nullable=False, index=True)
    actual_output_mt = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    rejected_output_mt = db.Column(db.Numeric(12, 3), nullable=False, default=0)
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
            "month_start": self.month_start.isoformat() if self.month_start else None,
            "machine_id": self.machine_id,
            "actual_output_mt": float(self.actual_output_mt or 0),
            "rejected_output_mt": float(self.rejected_output_mt or 0),
            "machine": self.machine.to_dict() if self.machine else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
