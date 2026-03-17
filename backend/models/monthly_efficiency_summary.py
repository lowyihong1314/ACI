from datetime import datetime

from backend.models.db import db


class MonthlyEfficiencySummary(db.Model):
    __tablename__ = "monthly_efficiency_summary"
    __table_args__ = (
        db.UniqueConstraint("scope_code", "month_start", name="uq_monthly_efficiency_summary"),
    )

    id = db.Column(db.Integer, primary_key=True)
    scope_code = db.Column(db.String(40), nullable=False, default="OVERALL", index=True)
    month_start = db.Column(db.Date, nullable=False, index=True)
    planned_output_mt = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    actual_output_mt = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    efficiency_ratio = db.Column(db.Numeric(10, 6), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "scope_code": self.scope_code,
            "month_start": self.month_start.isoformat() if self.month_start else None,
            "planned_output_mt": float(self.planned_output_mt or 0),
            "actual_output_mt": float(self.actual_output_mt or 0),
            "efficiency_ratio": float(self.efficiency_ratio)
            if self.efficiency_ratio is not None
            else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
