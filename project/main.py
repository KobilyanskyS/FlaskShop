from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from .admin import get_categories_hierarchically
from . import db
from .models import Product, Category, Cart

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

main = Blueprint('main', __name__)


@main.route('/')
def index():
    categories = get_categories_hierarchically()
    total_price = get_cart_total_price()
    return render_template('index.html', categories=categories, total_price=total_price)


@main.route('/profile')
@login_required
def profile():
    total_price = get_cart_total_price()
    return render_template('profile.html', name=current_user.name, total_price=total_price)


@main.route('/products')
def products():
    category_id = request.args.get('category_id')
    products_in_category = db.session.query(Product).join(Category).filter(Category.id == category_id).all()
    try:
        total_price = get_cart_total_price()
        cart = Cart.query.filter_by(user_id=current_user.id).all()
        cart_ids = [item.product_id for item in cart]
        return render_template('products.html', products=products_in_category, category_id=category_id,
                               total_price=total_price, cart=cart, cart_ids=cart_ids)
    except:
        return render_template('products.html', products=products_in_category, category_id=category_id)


@main.route('/product')
def get_product():
    product_id = request.args.get('product_id')
    if product_id is None:
        return redirect(url_for('main.index'))
    product = Product.query.get(product_id)
    try:
        total_price = get_cart_total_price()
        cart = Cart.query.filter_by(user_id=current_user.id).all()
        cart_ids = [item.product_id for item in cart]
        return render_template('product.html', product=product,
                               total_price=total_price, cart=cart, cart_ids=cart_ids)
    except:
        return render_template('product.html', total_price=total_price, product=product)


@main.route('/cart')
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

    return render_template('cart.html', total_price=total_price, cart_items=products_in_cart)


@main.route('/_add_item_to_cart', methods=['POST'])
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


@main.route('/_delete_item_from_cart', methods=['POST'])
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
