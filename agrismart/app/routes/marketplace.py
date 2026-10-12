from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Product, Order, OrderItem
import uuid
import datetime

marketplace_bp = Blueprint('marketplace', __name__)

@marketplace_bp.route('/')
@login_required
def index():
    """Marketplace home with tilting product cards, category filters, and search"""
    category = request.args.get('category', 'all')
    search = request.args.get('q', '').strip()
    
    query = Product.query.filter_by(is_active=True)
    if category != 'all':
        query = query.filter(Product.category.ilike(category))
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%") | Product.description.ilike(f"%{search}%"))
        
    products = query.order_by(Product.created_at.desc()).all()
    categories = ['All', 'Seeds', 'Fertilizer', 'Tools', 'Organic']
    
    return render_template('marketplace/index.html', products=products, categories=categories, current_category=category, search=search)

@marketplace_bp.route('/api/products')
@login_required
def get_products():
    """JSON API for products"""
    products = Product.query.filter_by(is_active=True).all()
    return jsonify({
        'success': True,
        'products': [p.to_dict() for p in products]
    })

@marketplace_bp.route('/cart')
@login_required
def cart():
    """Standalone Shopping Cart & Checkout Page"""
    return render_template('marketplace/cart.html')

@marketplace_bp.route('/api/checkout', methods=['POST'])
@login_required
def checkout():
    """
    Processes checkout with realistic payment gateway details, 
    free delivery for orders >= ₹500, stock updates, and Order creation.
    """
    try:
        data = request.get_json() or {}
        items = data.get('items', [])
        shipping = data.get('shipping', {})
        payment = data.get('payment', {})
        
        if not items:
            return jsonify({'success': False, 'message': 'Your cart is empty.'}), 400
            
        subtotal = 0.0
        order_items_to_add = []
        
        # Calculate subtotal and validate items
        for item in items:
            prod_id = item.get('id')
            qty = int(item.get('quantity', item.get('qty', 1)))
            product = Product.query.get(prod_id)
            if not product:
                continue
                
            unit_price = product.price
            item_total = unit_price * qty
            subtotal += item_total
            
            # Stock management
            if product.stock >= qty:
                product.stock -= qty
            else:
                product.stock = 0
                
            order_items_to_add.append({
                'product_id': product.id,
                'quantity': qty,
                'unit_price': unit_price
            })
            
        if not order_items_to_add:
            return jsonify({'success': False, 'message': 'No valid products in cart.'}), 400

        # Free delivery logic: ₹500 and above is FREE delivery (₹0.00), otherwise ₹50.00
        delivery_fee = 0.0 if subtotal >= 500.0 else 50.0
        total_amount = round(subtotal + delivery_fee, 2)
        
        # Realistic Transaction Reference ID
        txn_id = payment.get('transaction_id') or f"TXN-{uuid.uuid4().hex[:10].upper()}"
        payment_method = payment.get('method', 'UPI (Google Pay / PhonePe)')
        payment_status = 'Pending (COD)' if 'Cash on Delivery' in payment_method else 'Paid'
        
        # Generate clean human-readable order number
        order_number = f"AGR-{datetime.datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:5].upper()}"
        
        order = Order(
            user_id=current_user.id,
            order_number=order_number,
            status='Confirmed',
            total_amount=total_amount,
            shipping_name=shipping.get('name', current_user.display_name),
            shipping_address=shipping.get('address', 'Plot 42, Green Fields Road'),
            shipping_city=shipping.get('city', current_user.location or 'Pune'),
            shipping_phone=shipping.get('phone', current_user.phone or '+91 98765 43210'),
            payment_method=f"{payment_method} ({payment_status})",
            payment_status=payment_status
        )
        db.session.add(order)
        db.session.flush() # get order.id
        
        for item_data in order_items_to_add:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price']
            )
            db.session.add(order_item)
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order placed & payment processed successfully!',
            'order_number': order.order_number,
            'order_id': order.id,
            'subtotal': round(subtotal, 2),
            'delivery_fee': delivery_fee,
            'total_amount': order.total_amount,
            'payment_method': order.payment_method,
            'transaction_id': txn_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@marketplace_bp.route('/orders')
@login_required
def orders():
    """My Orders timeline and stepper view"""
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('marketplace/orders.html', orders=user_orders)

@marketplace_bp.route('/api/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    """Cancels a pending order"""
    order = Order.query.get_or_404(order_id)
    if order.user_id != current_user.id and not getattr(current_user, 'is_admin', False):
        return jsonify({'success': False, 'message': 'Unauthorized.'}), 403
        
    if order.status in ['Shipped', 'Delivered']:
        return jsonify({'success': False, 'message': f'Cannot cancel order in "{order.status}" status.'}), 400
        
    order.status = 'Cancelled'
    db.session.commit()
    return jsonify({'success': True, 'message': 'Order cancelled successfully.'})
