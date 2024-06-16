import os
import json
import random
from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_args
from extensions import db
from models import Product, Category, Order, OrderItem, User, Banners, IndexCategory

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
        abort(403)
    return render_template('admin/admin.html', name=current_user.name)


@admin.route('/shop_admin/categories/add', methods=['POST'])
@login_required
def add_category():
    if not current_user.is_admin:
        abort(403)
    name = request.form.get('name')
    main_category = request.form.get('main_category')

    if main_category == "":
        main_category = None

    new_category = Category(main_category=main_category, name=name)
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
            "level": category.level * "-",
            "main_category": category.main_category,
        } for category in categories
    ])

    return render_template(
        'admin/manage_products.html',
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

@admin.route('/shop_admin/orders')
@login_required
def manage_orders():
    if not current_user.is_admin:
        abort(403)

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    per_page = 20

    offset = (page - 1) * per_page

    orders_query = Order.query.order_by(Order.order_date.desc())
    total = orders_query.count()

    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap5', format_total='',
                            prev_label='<<', next_label='>>')

    orders = orders_query.limit(per_page).offset(offset).all()

    for order in orders:
        user = User.query.get(order.user_id)
        order.user_name = user.name

    return render_template('admin/manage_orders.html', orders=orders,
                           pagination=pagination, name=current_user.name)


@admin.route('/_switch_order_status_to_ready', methods=['POST'])
@login_required
def order_ready():
    if not current_user.is_admin:
        abort(403)
    if request.method == 'POST':
        order_id = int(request.form['order_id'])
        user_id = current_user.id

        order = Order.query.filter_by(id=order_id).first()
        if not order:
            return render_template('404.html'), 404

        order.status = "Заказ готов"
        db.session.commit()

        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@admin.route('/_switch_order_status_to_issued', methods=['POST'])
@login_required
def order_issued():
    if not current_user.is_admin:
        abort(403)
    if request.method == 'POST':
        order_id = int(request.form['order_id'])
        user_id = current_user.id

        order = Order.query.filter_by(id=order_id).first()
        if not order:
            return render_template('404.html'), 404

        order.status = "Заказ выдан"
        db.session.commit()

        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@admin.route('/shop_admin/orders/order_details')
@login_required
def show_order_details():
    if not current_user.is_admin:
        abort(403)
    order_id = request.args.get('order_id')

    order = Order.query.filter_by(id=order_id).first()
    if not order:
        return render_template('404.html'), 404

    user = User.query.get(order.user_id)
    order.user_name = user.name

    order_items = OrderItem.query.filter_by(order_id=order_id).all()

    items_info = []
    for item in order_items:
        product = Product.query.get(item.product_id)

        item_info = {
            'product_name': product.name,
            'product_image_url': product.image_url,
            'quantity': item.quantity,
            'price': product.price,
            'product_total_price': round(item.quantity * product.price, 2)
        }
        items_info.append(item_info)

    return render_template('admin/order_details.html', items=items_info, order=order)


@admin.route('/shop_admin/manage_index')
@login_required
def manage_index():
    if not current_user.is_admin:
        abort(403)
    banners = Banners.query.order_by(Banners.id.desc())
    categories = get_categories_hierarchically()
    index_category = IndexCategory.query.get(1)
    if index_category is not None:
        category_id = index_category.category_id
        cur_category = Category.query.get(category_id).name
        for banner in banners:
            category_name = Category.query.get(banner.category_id)
            banner.category_name = category_name.name
        return render_template('admin/manage_index.html', cur_category=cur_category, banners=banners, categories=categories, name=current_user.name)

    return render_template('admin/manage_index.html', cur_category='', banners=banners, categories=categories, name=current_user.name)

@admin.route('/shop_admin/manage_index/_add_banner',  methods=['POST'])
@login_required
def add_banner():
    if not current_user.is_admin:
        abort(403)
    if request.method == "POST":
        name = request.form.get('name')
        category_id = request.form.get('category_id')
        image_url = ''
        is_active = True
        if name or category_id is None:
            redirect(url_for('admin.manage_index'))
        if 'file' in request.files:
            image_url = save_file(folder="./project/static/banners/", file=request.files['file'])
        if image_url is None:
            redirect(url_for('admin.manage_index'))

        new_banner = Banners(name=name, image_url=image_url, category_id=category_id, is_active=is_active)

        db.session.add(new_banner)
        db.session.commit()
        return redirect(url_for('admin.manage_index'))


@admin.route('/shop_admin/manage_index/_switch_banner_activity', methods=['POST'])
@login_required
def switch_banner_activity():
    if not current_user.is_admin:
        abort(403)
    if request.method == 'POST':
        is_active = request.form['is_active'].lower() == 'true'

        banner_id = int(request.form['banner_id'])
        banner = Banners.query.get_or_404(banner_id)
        banner.is_active = not is_active
        db.session.commit()
        print(banner.is_active)
        item_info = {
            'is_active': banner.is_active
            }
        return item_info




@admin.route('/shop_admin/manage_index/_choose_category', methods=['POST'])
@login_required
def index_category():
    try:
        category_id = request.form.get('category_id')
    except:
        return render_template('404.html'), 404
    if not current_user.is_admin:
        abort(403)
    if request.method == "POST":
        index_category = IndexCategory.query.get(1)
        if index_category:
            index_category.category_id = category_id
        else:
            index_category = IndexCategory(id=1, category_id=category_id)
            db.session.add(index_category)
        db.session.commit()
    cur_category = Category.query.get(category_id)
    return cur_category.name
