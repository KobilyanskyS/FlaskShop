from flask import Flask, render_template
from extensions import db, migrate, login_manager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fdkjshfhjsdfdskfdsfdcbsjdkfdsdf'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")

@app.errorhandler(403)
def forbidden(e):
    return render_template("404.html")

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint)

from admin import admin as admin_blueprint
app.register_blueprint(admin_blueprint)

from shop import shop as shop_blueprint
app.register_blueprint(shop_blueprint)

from main import main as main_blueprint
app.register_blueprint(main_blueprint)
