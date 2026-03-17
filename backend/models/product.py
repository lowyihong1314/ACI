from datetime import datetime

from backend.models.db import db


class Product(db.Model):
    __tablename__ = "product"
    __table_args__ = (
        db.UniqueConstraint("part_code", "warehouse_code", name="uq_product_part_code_warehouse"),
    )

    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey("plant.id"), nullable=True, index=True)
    part_code = db.Column(db.String(120), nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False)
    product_class = db.Column(db.String(40), nullable=True, index=True)
    warehouse_code = db.Column(db.String(40), nullable=True, index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    plant = db.relationship("Plant", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "plant_id": self.plant_id,
            "part_code": self.part_code,
            "description": self.description,
            "product_class": self.product_class,
            "warehouse_code": self.warehouse_code,
            "is_active": self.is_active,
            "plant": self.plant.to_dict() if self.plant else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
