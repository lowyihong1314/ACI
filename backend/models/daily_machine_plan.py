from datetime import datetime

from backend.models.db import db


class DailyMachinePlan(db.Model):
    __tablename__ = "daily_machine_plan"
    __table_args__ = (
        db.UniqueConstraint("plan_date", "machine_id", name="uq_daily_machine_plan"),
    )

    id = db.Column(db.Integer, primary_key=True)
    plan_date = db.Column(db.Date, nullable=False, index=True)
    machine_id = db.Column(db.Integer, db.ForeignKey("machine.id"), nullable=False, index=True)
    planned_output_mt = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    standard_output_mt = db.Column(db.Numeric(12, 3), nullable=True)
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
            "plan_date": self.plan_date.isoformat() if self.plan_date else None,
            "machine_id": self.machine_id,
            "planned_output_mt": float(self.planned_output_mt or 0),
            "standard_output_mt": float(self.standard_output_mt or 0)
            if self.standard_output_mt is not None
            else None,
            "machine": self.machine.to_dict() if self.machine else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
