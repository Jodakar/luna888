from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Конфигурация
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'luna888-secret-key-2026')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://luna_user:LunaPass2026@localhost:5432/luna_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Инициализация
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = 'auth.login'
    
    # Регистрация Blueprint'ов
    from app.auth.routes import auth_bp
    from app.products.routes import products_bp
    from app.orders_mp.routes import orders_mp_bp
    from app.couriers.routes import couriers_bp
    from app.deliveries.routes import deliveries_bp
    from app.returns.routes import returns_bp
    from app.inventory.routes import inventory_bp
    from app.reports.routes import reports_bp
    from app.timesheet.routes import timesheet_bp
    from app.employees.routes import employees_bp
    from app.settings.routes import settings_bp
    from app.profile.routes import profile_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_mp_bp)
    app.register_blueprint(couriers_bp)
    app.register_blueprint(deliveries_bp)
    app.register_blueprint(returns_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(timesheet_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(profile_bp)
    
    return app
