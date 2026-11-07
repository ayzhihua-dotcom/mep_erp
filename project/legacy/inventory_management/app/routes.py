from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from .models import db, User, Product, InboundRecord, OutboundRecord, StockTake, ReturnRecord

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    total_products = Product.query.count()
    total_stock_value = db.session.query(db.func.sum(Product.price * Product.stock)).scalar() or 0
    low_stock_count = Product.query.filter(Product.stock <= Product.min_stock).count()
    today_inbound = InboundRecord.query.filter(db.func.date(InboundRecord.created_at) == datetime.utcnow().date()).count()
    today_outbound = OutboundRecord.query.filter(db.func.date(OutboundRecord.created_at) == datetime.utcnow().date()).count()
    
    recent_inbound = InboundRecord.query.order_by(InboundRecord.created_at.desc()).limit(5).all()
    recent_outbound = OutboundRecord.query.order_by(OutboundRecord.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         total_products=total_products,
                         total_stock_value=total_stock_value,
                         low_stock_count=low_stock_count,
                         today_inbound=today_inbound,
                         today_outbound=today_outbound,
                         recent_inbound=recent_inbound,
                         recent_outbound=recent_outbound)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('用户名或密码错误', 'error')
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# Product Management
@main.route('/products')
@login_required
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@main.route('/products/add', methods=['POST'])
@login_required
def add_product():
    data = request.form
    product = Product(
        code=data['code'],
        name=data['name'],
        category=data.get('category', ''),
        unit=data['unit'],
        price=float(data['price']),
        min_stock=int(data.get('min_stock', 0))
    )
    db.session.add(product)
    db.session.commit()
    flash('商品添加成功', 'success')
    return redirect(url_for('main.products'))

@main.route('/products/edit/<int:id>', methods=['POST'])
@login_required
def edit_product(id):
    product = Product.query.get_or_404(id)
    data = request.form
    product.code = data['code']
    product.name = data['name']
    product.category = data.get('category', '')
    product.unit = data['unit']
    product.price = float(data['price'])
    product.min_stock = int(data.get('min_stock', 0))
    db.session.commit()
    flash('商品更新成功', 'success')
    return redirect(url_for('main.products'))

@main.route('/products/delete/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('商品删除成功', 'success')
    return redirect(url_for('main.products'))

# Inbound Management
@main.route('/inbound')
@login_required
def inbound():
    records = InboundRecord.query.order_by(InboundRecord.created_at.desc()).all()
    products = Product.query.all()
    return render_template('inbound.html', records=records, products=products)

@main.route('/inbound/add', methods=['POST'])
@login_required
def add_inbound():
    data = request.form
    product = Product.query.get_or_404(int(data['product_id']))
    
    record = InboundRecord(
        product_id=int(data['product_id']),
        quantity=int(data['quantity']),
        price=float(data['price']),
        supplier=data.get('supplier', ''),
        note=data.get('note', ''),
        user_id=current_user.id
    )
    
    product.stock += int(data['quantity'])
    db.session.add(record)
    db.session.commit()
    flash('入库成功', 'success')
    return redirect(url_for('main.inbound'))

# Outbound Management
@main.route('/outbound')
@login_required
def outbound():
    records = OutboundRecord.query.order_by(OutboundRecord.created_at.desc()).all()
    products = Product.query.all()
    return render_template('outbound.html', records=records, products=products)

@main.route('/outbound/add', methods=['POST'])
@login_required
def add_outbound():
    data = request.form
    product = Product.query.get_or_404(int(data['product_id']))
    quantity = int(data['quantity'])
    
    if product.stock < quantity:
        flash('库存不足', 'error')
        return redirect(url_for('main.outbound'))
    
    record = OutboundRecord(
        product_id=int(data['product_id']),
        quantity=quantity,
        price=float(data['price']),
        customer=data.get('customer', ''),
        note=data.get('note', ''),
        user_id=current_user.id
    )
    
    product.stock -= quantity
    db.session.add(record)
    db.session.commit()
    flash('出库成功', 'success')
    return redirect(url_for('main.outbound'))

# Stock Query
@main.route('/stock')
@login_required
def stock():
    keyword = request.args.get('keyword', '')
    if keyword:
        products = Product.query.filter(
            db.or_(
                Product.code.contains(keyword),
                Product.name.contains(keyword),
                Product.category.contains(keyword)
            )
        ).all()
    else:
        products = Product.query.all()
    return render_template('stock.html', products=products, keyword=keyword)

# Stock Take
@main.route('/stocktake')
@login_required
def stocktake():
    records = StockTake.query.order_by(StockTake.created_at.desc()).all()
    products = Product.query.all()
    return render_template('stocktake.html', records=records, products=products)

@main.route('/stocktake/add', methods=['POST'])
@login_required
def add_stocktake():
    data = request.form
    product = Product.query.get_or_404(int(data['product_id']))
    actual_quantity = int(data['actual_quantity'])
    difference = actual_quantity - product.stock
    
    record = StockTake(
        product_id=int(data['product_id']),
        actual_quantity=actual_quantity,
        system_quantity=product.stock,
        difference=difference,
        note=data.get('note', ''),
        user_id=current_user.id
    )
    
    product.stock = actual_quantity
    db.session.add(record)
    db.session.commit()
    flash('盘点完成', 'success')
    return redirect(url_for('main.stocktake'))

# Returns
@main.route('/returns')
@login_required
def returns():
    records = ReturnRecord.query.order_by(ReturnRecord.created_at.desc()).all()
    products = Product.query.all()
    return render_template('returns.html', records=records, products=products)

@main.route('/returns/add', methods=['POST'])
@login_required
def add_return():
    data = request.form
    product = Product.query.get_or_404(int(data['product_id']))
    quantity = int(data['quantity'])
    return_type = data['return_type']
    
    record = ReturnRecord(
        product_id=int(data['product_id']),
        quantity=quantity,
        return_type=return_type,
        reason=data.get('reason', ''),
        user_id=current_user.id
    )
    
    if return_type == 'inbound':
        product.stock += quantity
    else:
        product.stock -= quantity
    
    db.session.add(record)
    db.session.commit()
    flash('退入库成功', 'success')
    return redirect(url_for('main.returns'))

# Reports
@main.route('/reports')
@login_required
def reports():
    start_date = request.args.get('start_date', (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d'))
    end_date = request.args.get('end_date', datetime.utcnow().strftime('%Y-%m-%d'))
    
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    
    inbound_records = InboundRecord.query.filter(
        InboundRecord.created_at.between(start, end)
    ).all()
    outbound_records = OutboundRecord.query.filter(
        OutboundRecord.created_at.between(start, end)
    ).all()
    
    total_inbound = sum(r.quantity for r in inbound_records)
    total_outbound = sum(r.quantity for r in outbound_records)
    inbound_value = sum(r.quantity * r.price for r in inbound_records)
    outbound_value = sum(r.quantity * r.price for r in outbound_records)
    
    return render_template('reports.html',
                         inbound_records=inbound_records,
                         outbound_records=outbound_records,
                         total_inbound=total_inbound,
                         total_outbound=total_outbound,
                         inbound_value=inbound_value,
                         outbound_value=outbound_value,
                         start_date=start_date,
                         end_date=end_date)

# User Management
@main.route('/users')
@login_required
def users():
    if current_user.role != 'admin':
        flash('无权限访问', 'error')
        return redirect(url_for('main.index'))
    users = User.query.all()
    return render_template('users.html', users=users)

@main.route('/users/add', methods=['POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('无权限操作', 'error')
        return redirect(url_for('main.index'))
    
    data = request.form
    if User.query.filter_by(username=data['username']).first():
        flash('用户名已存在', 'error')
        return redirect(url_for('main.users'))
    
    user = User(username=data['username'], role=data.get('role', 'user'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    flash('用户添加成功', 'success')
    return redirect(url_for('main.users'))

@main.route('/users/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    if current_user.role != 'admin':
        flash('无权限操作', 'error')
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(id)
    if user.username == 'admin':
        flash('不能删除管理员账户', 'error')
        return redirect(url_for('main.users'))
    
    db.session.delete(user)
    db.session.commit()
    flash('用户删除成功', 'success')
    return redirect(url_for('main.users'))

# API endpoints for AJAX
@main.route('/api/product/<int:id>')
@login_required
def get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'code': product.code,
        'name': product.name,
        'category': product.category,
        'unit': product.unit,
        'price': product.price,
        'stock': product.stock,
        'min_stock': product.min_stock
    })
