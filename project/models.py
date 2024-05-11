from flask_login import UserMixin
from sqlalchemy import CheckConstraint
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    created_on = db.Column(db.DateTime, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer)
    image_url = db.Column(db.String(255))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    main_category = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    image_url = db.Column(db.String(255))


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, CheckConstraint('quantity >= 0'))


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)
    total_price = db.Column(db.Float)
    status = db.Column(db.String(255), nullable=False)


class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, CheckConstraint('quantity >= 0'))


class Banners(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    image_url = db.Column(db.String(255), nullable=False, unique=True)