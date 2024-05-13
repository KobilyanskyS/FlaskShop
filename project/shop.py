from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from flask_paginate import Pagination, get_page_args
from sqlalchemy import or_
from . import db
from .models import Product, Category, Cart, Order, OrderItem

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

shop = Blueprint('shop', __name__)

@shop.route('/my_orders')
@login_required
def my_orders():
    total_price = get_cart_total_price()
    orders = Order.query.filter_by(user_id=current_user.id) \
        .order_by(Order.order_date.desc()) \
        .all()
    return render_template('shop/my_orders.html', total_price=total_price, orders=orders)

@shop.route('/search', methods=['POST'])
def search_products():
    if request.method == "POST":
        search_input = request.form.get('search_input').upper()

        if not search_input:
            return render_template('404.html'), 404

        results = Product.query.filter(or_(
            Product.name.ilike(f"%{search_input}%"),
            Product.description.ilike(f"%{search_input}%")
        )).all()

        return render_template('shop/search.html', products=results)

@shop.route('/order_info', methods=['POST'])
@login_required
def order_info():
    if request.method == "POST":
        user_id = current_user.id
        order_id = request.form.get('order_id')
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()

        if not order:
            return render_template('404.html'), 404

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

        return render_template('shop/order_info.html', items=items_info, order=order)


@shop.route('/products')
def products():
    category_id = request.args.get('category_id')
    products_in_category = db.session.query(Product).join(Category).filter(Category.id == category_id).all()

    total = len(products_in_category)

    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    per_page = 20
    offset = (page - 1) * per_page
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap5', format_total='',
                            prev_label='<<', next_label='>>')

    products_in_category = db.session.query(Product).join(Category).filter(Category.id == category_id).limit(
        per_page).offset(offset).all()

    if not products_in_category:
        return render_template('404.html'), 404
    try:
        cart = Cart.query.filter_by(user_id=current_user.id).all()
        cart_ids = [item.product_id for item in cart]
        return render_template('shop/products.html', products=products_in_category, category_id=category_id, cart=cart,
                               cart_ids=cart_ids, pagination=pagination)
    except:
        return render_template('shop/products.html', products=products_in_category, category_id=category_id,
                               pagination=pagination)

@shop.route('/product')
def get_product():
    product_id = request.args.get('product_id')
    if product_id is None:
        return render_template('404.html'), 404
    product = Product.query.get(product_id)
    if not product:
        return render_template('404.html'), 404
    try:
        cart = Cart.query.filter_by(user_id=current_user.id).all()
        cart_ids = [item.product_id for item in cart]
        return render_template('product.html', product=product,
                                cart=cart, cart_ids=cart_ids)
    except:
        return render_template('shop/product.html', product=product)


@shop.route('/cart')
@login_required
def cart():
    total_price = get_cart_total_price()

    cart_items = Cart.query.filter_by(user_id=current_user.id).all()

    products_in_cart = []
    for item in cart_items:
        product = Product.query.get(item.product_id)
        product_data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'quantity': item.quantity,
            'image_url': product.image_url
        }
        products_in_cart.append(product_data)

    return render_template('shop/cart.html', total_price=total_price, cart_items=products_in_cart)


@shop.route('/order')
@login_required
def order():
    user_id = current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    order_data = []
    total_price = get_cart_total_price()

    for item in cart_items:
        product = Product.query.get(item.product_id)
        item_total_price = product.price * item.quantity

        order_data.append({
            'product_name': product.name,
            'product_image_url': product.image_url,
            'product_price': product.price,
            'quantity': item.quantity,
            'item_total_price': item_total_price
        })

    return render_template('shop/create_order.html', order_data=order_data, total_price=total_price)


@shop.route('/create_order')
@login_required
def create_order():
    user_id = current_user.id
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    total_price = get_cart_total_price()

    order = Order(user_id=user_id, order_date=datetime.now(),
                  total_price=total_price, status="Заказ создан")
    db.session.add(order)
    db.session.flush()

    for item in cart_items:
        order_item = OrderItem(order_id=order.id, user_id=user_id,
                               product_id=item.product_id, quantity=item.quantity)
        db.session.add(order_item)

    Cart.query.filter_by(user_id=user_id).delete()

    db.session.commit()

    return redirect(url_for('shop.my_orders'))


@shop.route('/cancel_order', methods=['POST'])
@login_required
def cancel_order():
    if request.method == "POST":
        order_id = request.form.get('order_id')
        order = Order.query.get_or_404(order_id)
        order.status = "Заказ отменён"
        db.session.commit()

    return redirect(url_for('shop.my_orders'))


@shop.route('/_add_item_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        quantity = int(request.form['quantity'])
        user_id = current_user.id

        existing_item = Cart.query.filter_by(
            user_id=user_id, product_id=product_id
        ).first()

        if existing_item:
            existing_item.quantity += quantity
        else:
            new_cart_item = Cart(user_id=user_id, product_id=product_id, quantity=1)
            db.session.add(new_cart_item)

        db.session.commit()

        total_price = get_cart_total_price()
        product_quantity = existing_item.quantity if existing_item else 1

        data = {
            'quantity': product_quantity,
            'total_value': total_price
        }

        if product_quantity <= 0:
            db.session.delete(existing_item)
            db.session.commit()
            data = {
                'quantity': 0,
                'total_value': total_price
            }
            return jsonify(data)

        return jsonify(data)


@login_required
def get_cart_total_price():
    total_value = 0
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    for item in cart_items:
        product = Product.query.get(item.product_id)
        total_value += product.price * item.quantity

    return round(total_value, 2)


@shop.route('/_delete_item_from_cart', methods=['POST'])
@login_required
def _delete_item_from_cart():
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        user_id = current_user.id
        existing_item = Cart.query.filter_by(
            user_id=user_id, product_id=product_id
        ).first()

        db.session.delete(existing_item)
        db.session.commit()

    total_price = get_cart_total_price()

    return str(total_price)