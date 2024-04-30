from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .admin import get_categories_hierarchically
from . import db
from .models import Product, Category

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

main = Blueprint('main', __name__)


@main.route('/')
def index():
    categories = get_categories_hierarchically()
    return render_template('index.html', categories=categories)


@main.route('/products')
def products():
    category_id = request.args.get('category_id')
    products_in_category = db.session.query(Product).join(Category).filter(Category.id == category_id).all()
    return render_template('products.html', products=products_in_category, category_id=category_id)


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)