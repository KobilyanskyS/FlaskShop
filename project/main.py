import os
from flask import Blueprint, render_template, abort, request, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from . import db
from .models import Product, Category

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(folder, file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(folder, filename)
        file.save(file_path)
        relative_path = os.path.relpath(file_path, start=os.path.join(os.getcwd(), 'project'))
        return f"/{relative_path.replace(os.sep, '/')}"
    else:
        return None


@main.route('/shop_admin')
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)  # Access denied
    return render_template('admin.html', name=current_user.name)


@main.route('/shop_admin/categories/add', methods=['POST'])
@login_required
def add_category():
    if not current_user.is_admin:
        abort(403)
    name = request.form.get('name')
    main_category = request.form.get('main_category')
    image_url = ''

    if 'file' in request.files:
        image_url = save_file(folder="./project/static/categories/", file=request.files['file'])
    if image_url is None:
        image_url = '/static/categories/default_category.png'

    if main_category == "":
        main_category = None

    new_category = Category(main_category=main_category, name=name, image_url=image_url)
    db.session.add(new_category)
    db.session.commit()
    return redirect(url_for('main.manage_products'))


@main.route('/shop_admin/categories/edit')
@login_required
def edit_category():
    return "Хуй"


@main.route('/shop_admin/categories/delete')
@login_required
def delete_category():
    return "Хуй2"


@main.route('/shop_admin/products')
@login_required
def manage_products():
    if not current_user.is_admin:
        abort(403)
    products = db.session.query(Product, Category.name) \
        .join(Category, Product.category_id == Category.id) \
        .all()
    categories = get_categories_hierarchically()
    return render_template('manage_products.html', products=products, categories=categories, name=current_user.name)


def get_categories_hierarchically(parent_id=None, level=0):
    categories = Category.query.filter_by(main_category=parent_id).all()
    result = []
    for category in categories:
        category.level = level
        result.append(category)
        result.extend(get_categories_hierarchically(category.id, level + 1))
    return result


@main.route('/shop_admin/products/edit')
@login_required
def edit_product():
    return "Хуй3"


@main.route('/shop_admin/products/delete')
@login_required
def delete_product():
    return "Хуй4"


@main.route('/shop_admin/products/add', methods=['POST'])
@login_required
def add_product():
    if not current_user.is_admin:
        abort(403)
    name = request.form.get('name')
    description = request.form.get('description')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    image_url = ''

    if 'file' in request.files:
        image_url = save_file(folder="./project/static/products/", file=request.files['file'])
    if image_url is None:
        image_url = '/static/products/default_product.png'

    category_id = request.form.get('category_id')

    new_product = Product(name=name, description=description, price=price, quantity=quantity,
                          image_url=image_url, category_id=category_id)
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('main.manage_products'))
