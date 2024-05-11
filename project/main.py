from flask import Blueprint, render_template
from .admin import get_categories_hierarchically
from .models import Banners

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

main = Blueprint('main', __name__)


@main.route('/')
def index():
    categories = get_categories_hierarchically()
    banners = Banners.query.order_by(Banners.id.desc())

    return render_template('shop/index.html', categories=categories, banners=banners, enumerate=enumerate)


