from flask import Blueprint, render_template
from .admin import get_categories_hierarchically
from .models import Banners, IndexCategory, Product, Category, Cart
from flask_login import current_user
from flask_paginate import Pagination, get_page_args
from . import db

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

main = Blueprint('main', __name__)


@main.route('/')
def index():
    categories = get_categories_hierarchically()
    banners = Banners.query.filter_by(is_active=True).order_by(Banners.id.desc())

    category = IndexCategory.query.get(1)
    if category is not None:
        category_id = category.category_id
        cur_category = Category.query.get(category_id)
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

        try:
            cart = Cart.query.filter_by(user_id=current_user.id).all()
            cart_ids = [item.product_id for item in cart]

            return render_template('shop/index.html', categories=categories, cur_category=cur_category,
                               products=products_in_category, cart=cart, cart_ids=cart_ids, banners=banners,
                               enumerate=enumerate, pagination=pagination)
        except:
            return render_template('shop/index.html', categories=categories, cur_category=cur_category,
                                   products=products_in_category, banners=banners,
                                   enumerate=enumerate, pagination=pagination)

    return render_template('shop/index.html', categories=categories, cur_category='',
                                   products=[], banners=banners,
                                   enumerate=enumerate, pagination='')

