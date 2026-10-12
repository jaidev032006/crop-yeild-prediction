from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response, session
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import Admin, User, Order, Prediction, Feedback, Product
import csv
import io
import datetime
from functools import wraps

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not isinstance(current_user, Admin):
            flash('Access restricted to AgriSmart Control Room operators.', 'error')
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Dark Control Room Login"""
    if current_user.is_authenticated and isinstance(current_user, Admin):
        return redirect(url_for('admin.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.check_password(password):
            if not admin.is_active:
                flash('This administrator account has been disabled.', 'error')
                return redirect(url_for('admin.login'))
                
            login_user(admin)
            flash('Welcome to the AgriSmart Control Room.', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials. Access attempt logged.', 'error')
            
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    logout_user()
    flash('Control room session ended.', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Dark Control Room Dashboard with KPIs, tables, and live controls"""
    users = User.query.order_by(User.created_at.desc()).all()
    orders = Order.query.order_by(Order.created_at.desc()).all()
    predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(50).all()
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    products = Product.query.all()
    
    total_revenue = sum(o.total_amount for o in orders if o.status != 'Cancelled')
    
    # Calculate daily prediction counts for chart
    today = datetime.date.today()
    chart_dates = [(today - datetime.timedelta(days=i)).strftime('%b %d') for i in range(6, -1, -1)]
    chart_predictions = [Prediction.query.filter(
        db.func.date(Prediction.created_at) == (today - datetime.timedelta(days=i))
    ).count() for i in range(6, -1, -1)]
    
    chart_orders = [Order.query.filter(
        db.func.date(Order.created_at) == (today - datetime.timedelta(days=i))
    ).count() for i in range(6, -1, -1)]
    
    return render_template(
        'admin/dashboard.html',
        admin=current_user,
        users=users,
        orders=orders,
        predictions=predictions,
        feedbacks=feedbacks,
        products=products,
        total_revenue=total_revenue,
        total_users=len(users),
        total_orders=len(orders),
        total_predictions=Prediction.query.count(),
        total_feedback=len(feedbacks),
        chart_dates=chart_dates,
        chart_predictions=chart_predictions,
        chart_orders=chart_orders
    )

@admin_bp.route('/api/change-password', methods=['POST'])
@admin_required
def change_password():
    """Change admin password and clear force_change_password flag"""
    try:
        data = request.get_json() or {}
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters.'}), 400
        if new_password != confirm_password:
            return jsonify({'success': False, 'message': 'Passwords do not match.'}), 400
            
        current_user.set_password(new_password)
        current_user.force_change_password = False
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Admin password updated successfully!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/api/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Activates or deactivates user"""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': user.is_active, 'message': f'User is now {"active" if user.is_active else "inactive"}.'})

@admin_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Deletes user account"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'success': True, 'message': 'User deleted successfully.'})

@admin_bp.route('/api/orders/<int:order_id>/update-status', methods=['POST'])
@admin_required
def update_order_status(order_id):
    """Updates order status via AJAX without reload"""
    data = request.get_json() or {}
    new_status = data.get('status')
    
    valid_statuses = ['Pending', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'message': 'Invalid order status.'}), 400
        
    order = Order.query.get_or_404(order_id)
    order.status = new_status
    db.session.commit()
    
    return jsonify({'success': True, 'status': order.status, 'message': f'Order status updated to {new_status}.'})

@admin_bp.route('/api/feedback/<int:feedback_id>/toggle-public', methods=['POST'])
@admin_required
def toggle_feedback_public(feedback_id):
    """Toggles public testimonial visibility"""
    feedback = Feedback.query.get_or_404(feedback_id)
    feedback.is_public = not feedback.is_public
    db.session.commit()
    return jsonify({'success': True, 'is_public': feedback.is_public, 'message': f'Feedback is now {"public" if feedback.is_public else "hidden"}.'})

@admin_bp.route('/api/export-orders')
@admin_required
def export_orders():
    """Exports all customer orders to CSV format"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'Order #', 'Date & Time', 'Customer Name', 'Phone', 'City', 'Delivery Address',
        'Items Purchased', 'Total Items Qty', 'Total Amount (INR)', 'Payment Method', 'Payment Status', 'Order Status'
    ])
    
    orders = Order.query.order_by(Order.created_at.desc()).all()
    for o in orders:
        items_summary = "; ".join([f"{item.product.name if item.product else 'Product'} (x{item.quantity})" for item in o.items])
        total_qty = sum(item.quantity for item in o.items)
        writer.writerow([
            o.order_number, o.created_at.strftime('%Y-%m-%d %H:%M:%S'), o.shipping_name,
            o.shipping_phone, o.shipping_city, o.shipping_address,
            items_summary, total_qty, f"{o.total_amount:.2f}",
            o.payment_method, o.payment_status, o.status
        ])
        
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=AgriSmart_Farmer_Orders_{datetime.date.today()}.csv"}
    )

@admin_bp.route('/api/export-predictions')
@admin_required
def export_predictions():
    """Exports all predictions to CSV format"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        'Prediction ID', 'User ID', 'Username', 'Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)',
        'Temperature (°C)', 'Humidity (%)', 'pH', 'Rainfall (mm)', 'Predicted Crop',
        'Confidence (%)', 'Yield Estimate (t/ha)', 'Yield Efficiency (%)', 'Date & Time'
    ])
    
    predictions = Prediction.query.order_by(Prediction.created_at.desc()).all()
    for p in predictions:
        username = p.user.username if p.user else 'Unknown'
        writer.writerow([
            p.id, p.user_id, username, p.nitrogen, p.phosphorus, p.potassium,
            p.temperature, p.humidity, p.ph, p.rainfall, p.predicted_crop,
            p.confidence, p.yield_estimate, p.yield_efficiency, p.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
        
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=AgriSmart_Predictions_Log_{datetime.date.today()}.csv"}
    )
