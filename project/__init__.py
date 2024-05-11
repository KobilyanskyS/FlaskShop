from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'fdkjshfhjsdfdskfdsfdcbsjdkfdsdf'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    migrate = Migrate(app, db, render_as_batch=False)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html")

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("404.html")

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    from .shop import shop as shop_blueprint
    app.register_blueprint(shop_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
