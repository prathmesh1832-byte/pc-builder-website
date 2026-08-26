from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Product, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pcbuilder.db'
app.config['SECRET_KEY'] = 'change-this-to-something-random-later'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    featured = Product.query.limit(4).all()
    return render_template('home.html', featured=featured)


@app.route('/products')
def products():
    all_products = Product.query.all()
    return render_template('products.html', products=all_products)


@app.route('/build', methods=['GET', 'POST'])
def build():
    categories = ['CPU', 'Motherboard', 'RAM', 'GPU', 'PSU', 'Storage', 'Case']
    products_by_category = {c: Product.query.filter_by(category=c).all() for c in categories}

    selected = {}
    issues = []

    if request.method == 'POST':
        for c in categories:
            product_id = request.form.get(c)
            selected[c] = Product.query.get(int(product_id)) if product_id else None

        cpu = selected.get('CPU')
        mobo = selected.get('Motherboard')
        ram = selected.get('RAM')
        gpu = selected.get('GPU')
        psu = selected.get('PSU')

        if cpu and mobo:
            if cpu.socket_type != mobo.socket_type:
                issues.append(f"CPU socket ({cpu.socket_type}) does not match Motherboard socket ({mobo.socket_type}).")

        if ram and mobo:
            if ram.ram_type != mobo.ram_type:
                issues.append(f"RAM type ({ram.ram_type}) is not supported by the Motherboard ({mobo.ram_type}).")

        if psu:
            total_power = 0
            if cpu and cpu.wattage:
                total_power += cpu.wattage
            if gpu and gpu.wattage:
                total_power += gpu.wattage
            required = total_power * 1.2
            if psu.wattage < required:
                issues.append(f"PSU wattage ({psu.wattage}W) may be insufficient. Recommended at least {int(required)}W.")

    return render_template('build.html', products_by_category=products_by_category,
                            selected=selected, issues=issues)

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    from models import CartItem

    categories = ['CPU', 'Motherboard', 'RAM', 'GPU', 'PSU', 'Storage', 'Case']
    added_count = 0

    for c in categories:
        product_id = request.form.get(c)
        if product_id:
            existing = CartItem.query.filter_by(user_id=current_user.id, product_id=int(product_id)).first()
            if existing:
                existing.quantity += 1
            else:
                new_item = CartItem(user_id=current_user.id, product_id=int(product_id), quantity=1)
                db.session.add(new_item)
            added_count += 1

    db.session.commit()
    flash(f'{added_count} component(s) added to your cart!')
    return redirect(url_for('cart'))


@app.route('/cart')
@login_required
def cart():
    from models import CartItem
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in items)
    return render_template('cart.html', items=items, total=total)

@app.route('/admin')
@admin_required
def admin_dashboard():
    from models import Order
    all_products = Product.query.all()
    all_orders = Order.query.all()
    return render_template('admin_dashboard.html', products=all_products, orders=all_orders)


@app.route('/admin/add_product', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    if request.method == 'POST':
        new_product = Product(
            name=request.form.get('name'),
            category=request.form.get('category'),
            brand=request.form.get('brand'),
            price=float(request.form.get('price')),
            stock=int(request.form.get('stock')),
            image=request.form.get('image'),
            socket_type=request.form.get('socket_type') or None,
            ram_type=request.form.get('ram_type') or None,
            form_factor=request.form.get('form_factor') or None,
            wattage=int(request.form.get('wattage')) if request.form.get('wattage') else None
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_add_product.html')

@app.route('/admin/edit_product/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        product.name = request.form.get('name')
        product.category = request.form.get('category')
        product.brand = request.form.get('brand')
        product.price = float(request.form.get('price'))
        product.stock = int(request.form.get('stock'))
        product.image = request.form.get('image')
        product.socket_type = request.form.get('socket_type') or None
        product.ram_type = request.form.get('ram_type') or None
        product.form_factor = request.form.get('form_factor') or None
        product.wattage = int(request.form.get('wattage')) if request.form.get('wattage') else None

        db.session.commit()
        flash('Product updated successfully!')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_edit_product.html', product=product)

@app.route('/admin/delete_product/<int:product_id>')
@admin_required
def admin_delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.')
    return redirect(url_for('admin_dashboard'))

@app.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    from models import CartItem
    item = CartItem.query.get_or_404(item_id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('cart'))


@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    from models import CartItem, Order, OrderItem

    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash('Your cart is empty.')
        return redirect(url_for('cart'))

    total = sum(item.product.price * item.quantity for item in items)
    new_order = Order(user_id=current_user.id, total_price=total, status='Placed')
    db.session.add(new_order)
    db.session.commit()

    for item in items:
        order_item = OrderItem(order_id=new_order.id, product_id=item.product_id,
                                quantity=item.quantity, price_at_purchase=item.product.price)
        db.session.add(order_item)
        db.session.delete(item)

    db.session.commit()
    flash('Order placed successfully!')
    return redirect(url_for('order_confirmation', order_id=new_order.id))


@app.route('/order_confirmation/<int:order_id>')
@login_required
def order_confirmation(order_id):
    from models import Order
    order = Order.query.get_or_404(order_id)
    return render_template('order_confirmation.html', order=order)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with that email already exists.')
            return redirect(url_for('signup'))

        new_user = User(name=name, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created! Please log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('products'))
        else:
            flash('Invalid email or password.')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


import os

with app.app_context():
    db.create_all()
    from models import Product
    if Product.query.count() == 0:
        import add_data
        
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)