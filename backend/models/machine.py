from datetime import datetime

from backend.models.db import db


class Machine(db.Model):
    __tablename__ = "machine"

    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey("plant.id"), nullable=False, index=True)
    code = db.Column(db.String(40), nullable=False, unique=True, index=True)
    name = db.Column(db.String(120), nullable=False)
    machine_group = db.Column(db.String(120), nullable=True)
    display_order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    supports_output = db.Column(db.Boolean, nullable=False, default=True)
    supports_reject = db.Column(db.Boolean, nullable=False, default=True)
    supports_breakdown = db.Column(db.Boolean, nullable=False, default=True)
    supports_efficiency = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    plant = db.relationship("Plant", back_populates="machines", lazy="joined")

    def to_dict(self):
        return {
            "id": self.id,
            "plant_id": self.plant_id,
            "code": self.code,
            "name": self.name,
            "machine_group": self.machine_group,
            "display_order": self.display_order,
            "is_active": self.is_active,
            "supports_output": self.supports_output,
            "supports_reject": self.supports_reject,
            "supports_breakdown": self.supports_breakdown,
            "supports_efficiency": self.supports_efficiency,
            "plant": self.plant.to_dict() if self.plant else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
