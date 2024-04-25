import os
import json
import random
from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from . import db
from .models import Product, Category

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

admin = Blueprint('admin', __name__)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(folder, file):
    if file and allowed_file(file.filename):
        random_name = generate_random_name()
        _, ext = os.path.splitext(file.filename)
        filename = f"{random_name}{ext}"
        file_path = os.path.join(folder, filename)
        file.save(file_path)
        relative_path = os.path.relpath(file_path, start=os.path.join(os.getcwd(), 'project'))
        return f"/{relative_path.replace(os.sep, '/')}"
    else:
        return None


def generate_random_name():
    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    random_name = ''
    for i in range(16):
        random_name += random.choice(characters)
    return random_name


@admin.route('/shop_admin')
@login_required
def shop_admin():
    if not current_user.is_admin:
        abort(403)  # Access denied
    return render_template('admin.html', name=current_user.name)


@admin.route('/shop_admin/categories/add', methods=['POST'])
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
    return redirect(url_for('admin.manage_products'))


@admin.route('/shop_admin/categories/edit', methods=['POST'])
@login_required
def edit_category():
    if not current_user.is_admin:
        abort(403)

    category_id = request.form.get('update_category_id')
    category = Category.query.get_or_404(category_id)

    name = request.form.get('update_category_name')
    main_category = request.form.get('update_category_main_category')

    if 'file' in request.files:
        new_image_url = save_file(folder="./project/static/categories/", file=request.files['file'])
        if new_image_url:
            category.image_url = new_image_url

    if main_category != '':
        category.main_category = main_category

    category.name = name

    db.session.commit()
    return redirect(url_for('admin.manage_products'))


@admin.route('/shop_admin/categories/delete', methods=['POST'])
@login_required
def delete_category():
    if not current_user.is_admin:
        abort(403)
    category_id = request.form.get('category_id')
    category = Category.query.get_or_404(category_id)

    f = category.image_url

    if f != '/static/categories/default_category.png':
        os.remove('./project'+f)

    db.session.delete(category)
    db.session.commit()

    return redirect(url_for('admin.manage_products'))


@admin.route('/shop_admin/products')
@login_required
def manage_products():
    if not current_user.is_admin:
        abort(403)
    products = db.session.query(Product, Category.name) \
        .join(Category, Product.category_id == Category.id) \
        .all()

    # Преобразуем данные в JSON
    products_json = json.dumps([
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "quantity": product.quantity,
            "category_name": category_name,
            "image_url": product.image_url
        } for product, category_name in products
    ])

    categories = get_categories_hierarchically()
    categories_json = json.dumps([
        {
            "id": category.id,
            "name": category.name,
            "level": category.level,
            "main_category": category.main_category,
            "image_url": category.image_url
        } for category in categories
    ])

    return render_template(
        'manage_products.html',
        products_json=products_json,
        categories_json=categories_json,
        name=current_user.name,
        categories=categories
    )


def get_categories_hierarchically(parent_id=None, level=0):
    categories = Category.query.filter_by(main_category=parent_id).all()
    result = []
    for category in categories:
        category.level = level
        result.append(category)
        result.extend(get_categories_hierarchically(category.id, level + 1))
    return result


@admin.route('/shop_admin/products/edit', methods=['POST'])
@login_required
def edit_product():
    if not current_user.is_admin:
        abort(403)

    product_id = request.form.get('update_product_id')
    product = Product.query.get_or_404(product_id)

    name = request.form.get('update_product_name')
    description = request.form.get('update_product_description')
    price = request.form.get('update_product_price')
    quantity = request.form.get('update_product_quantity')
    category_id = request.form.get('update_product_category_name')

    if 'file' in request.files:
        new_image_url = save_file(folder="./project/static/products/", file=request.files['file'])
        if new_image_url:
            product.image_url = new_image_url

    product.name = name
    product.description = description
    product.price = price
    product.quantity = quantity
    product.category_id = category_id

    db.session.commit()
    return redirect(url_for('admin.manage_products'))


@admin.route('/shop_admin/products/delete', methods=['POST'])
@login_required
def delete_product():
    if not current_user.is_admin:
        abort(403)
    product_id = request.form.get('product_id')
    product = Product.query.get_or_404(product_id)

    f = product.image_url

    if f != '/static/products/default_product.png':
        os.remove('./project'+f)

    db.session.delete(product)
    db.session.commit()

    return redirect(url_for('admin.manage_products'))


@admin.route('/shop_admin/products/add', methods=['POST'])
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
    return redirect(url_for('admin.manage_products'))
