from datetime import datetime

from backend.models.db import db


class AnnualMachineTarget(db.Model):
    __tablename__ = "annual_machine_target"
    __table_args__ = (
        db.UniqueConstraint("year", "machine_id", name="uq_annual_machine_target"),
    )

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    machine_id = db.Column(db.Integer, db.ForeignKey("machine.id"), nullable=False, index=True)
    annual_target_mt = db.Column(db.Numeric(12, 3), nullable=False, default=0)
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
            "year": self.year,
            "machine_id": self.machine_id,
            "annual_target_mt": float(self.annual_target_mt or 0),
            "machine": self.machine.to_dict() if self.machine else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
