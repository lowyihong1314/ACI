import os

from dotenv import load_dotenv
from flask import Flask, jsonify, send_file, send_from_directory
from flask_cors import CORS
from sqlalchemy import inspect
from werkzeug.security import generate_password_hash

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from backend.config import get_config
from backend.function.auth.current_user import auth_bp
from backend.function.auth.login import login_bp
from backend.function.auth.profile import profile_bp
from backend.function.production_daily import production_daily_bp
from backend.function.production_master import production_master_bp
from backend.function.production_reports import production_reports_bp
from backend.function.production import production_bp
from backend.models import Machine, Plant, UserData
from backend.models.db import db, jwt


def _register_extensions(app: Flask) -> None:
    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=False,
    )
    db.init_app(app)
    jwt.init_app(app)


def _register_blueprints(app: Flask) -> None:
    app.register_blueprint(login_bp, url_prefix="/api/auth")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(profile_bp, url_prefix="/api/auth")
    app.register_blueprint(production_bp, url_prefix="/api/production")
    app.register_blueprint(production_master_bp, url_prefix="/api")
    app.register_blueprint(production_daily_bp, url_prefix="/api")
    app.register_blueprint(production_reports_bp, url_prefix="/api")


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"message": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(_error):
        return jsonify({"message": "Internal server error"}), 500


def _ensure_default_user(app: Flask) -> None:
    default_username = app.config["DEFAULT_ADMIN_USERNAME"]
    default_password = app.config["DEFAULT_ADMIN_PASSWORD"]

    if not default_username or not default_password:
        return

    existing_user = UserData.query.filter_by(username=default_username).first()
    if existing_user:
        return

    db.session.add(
        UserData(
            username=default_username,
            full_name="System Administrator",
            password_hash=generate_password_hash(default_password),
            email="admin@example.com",
            is_admin=True,
        )
    )
    db.session.commit()


def _ensure_production_seed_data() -> None:
    inspector = inspect(db.engine)
    required_tables = {"plant", "machine"}
    if not required_tables.issubset(set(inspector.get_table_names())):
        return

    if Plant.query.first() or Machine.query.first():
        return

    plants = [
        Plant(code="ACI", name="ACI / Suasa Plant"),
        Plant(code="RS", name="RS / Keluli Plant"),
    ]
    db.session.add_all(plants)
    db.session.flush()

    plant_map = {item.code: item for item in plants}
    db.session.add_all(
        [
            Machine(plant_id=plant_map["ACI"].id, code="530A", name="530A", machine_group="Group A", display_order=10),
            Machine(plant_id=plant_map["ACI"].id, code="530B", name="530B", machine_group="Group A", display_order=20),
            Machine(plant_id=plant_map["ACI"].id, code="570", name="570", machine_group="Group A", display_order=30),
            Machine(plant_id=plant_map["ACI"].id, code="M8", name="M8", machine_group="Group A", display_order=40),
            Machine(plant_id=plant_map["ACI"].id, code="MPL", name="MPL", machine_group="Group A", display_order=50),
            Machine(plant_id=plant_map["ACI"].id, code="SPL", name="SPL", machine_group="Group A", display_order=60),
            Machine(plant_id=plant_map["RS"].id, code="530C", name="530C", machine_group="Group B", display_order=70),
            Machine(plant_id=plant_map["RS"].id, code="M16", name="M16", machine_group="Group B", display_order=80),
            Machine(plant_id=plant_map["RS"].id, code="MANUAL", name="Manual Keluli", machine_group="Group B", display_order=90),
        ]
    )
    db.session.commit()


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(get_config(config_name))
    dist_dir = os.path.join(os.path.dirname(__file__), "static", "dist")
    dist_index_path = os.path.join(dist_dir, "index.html")

    _register_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)

    @app.get("/")
    def serve_frontend_index():
        return send_file(dist_index_path)

    @app.get("/assets/<path:filename>")
    def serve_frontend_assets(filename: str):
        return send_from_directory(os.path.join(dist_dir, "assets"), filename)

    @app.get("/vite.svg")
    def serve_frontend_vite_icon():
        return send_from_directory(dist_dir, "vite.svg")

    @app.get("/api/health")
    def health_check():
        return jsonify(
            {
                "status": "ok",
                "environment": app.config["ENV_NAME"],
            }
        )

    with app.app_context():
        _ensure_default_user(app)
        _ensure_production_seed_data()

    return app
