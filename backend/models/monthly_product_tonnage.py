from datetime import datetime

from backend.models.db import db


class MonthlyProductTonnage(db.Model):
    __tablename__ = "monthly_product_tonnage"
    __table_args__ = (
        db.UniqueConstraint("month_start", "product_id", name="uq_monthly_product_tonnage"),
    )

    id = db.Column(db.Integer, primary_key=True)
    month_start = db.Column(db.Date, nullable=False, index=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False, index=True)
    output_mt = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    product = db.relationship("Product", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "month_start": self.month_start.isoformat() if self.month_start else None,
            "product_id": self.product_id,
            "output_mt": float(self.output_mt or 0),
            "product": self.product.to_dict() if self.product else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
