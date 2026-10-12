from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import User, Prediction, Order

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/')
@login_required
def index():
    """Profile overview and tabs"""
    predictions = Prediction.query.filter_by(user_id=current_user.id).order_by(Prediction.created_at.desc()).all()
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    
    return render_template(
        'profile/index.html',
        user=current_user,
        predictions=predictions,
        orders=orders
    )

@profile_bp.route('/api/update', methods=['POST'])
@login_required
def update_profile():
    """Updates user information"""
    try:
        data = request.get_json() or {}
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone = data.get('phone', '').strip()
        location = data.get('location', '').strip()
        bio = data.get('bio', '').strip()
        avatar_url = data.get('avatar_url', '').strip()
        
        current_user.first_name = first_name
        current_user.last_name = last_name
        current_user.phone = phone
        current_user.location = location
        current_user.bio = bio
        if avatar_url:
            current_user.avatar_url = avatar_url
            
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated successfully!', 'user': current_user.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@profile_bp.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    """Changes user password"""
    try:
        data = request.get_json() or {}
        current_pwd = data.get('current_password', '')
        new_pwd = data.get('new_password', '')
        confirm_pwd = data.get('confirm_password', '')
        
        if not current_user.check_password(current_pwd):
            return jsonify({'success': False, 'message': 'Incorrect current password.'}), 400
            
        if len(new_pwd) < 6:
            return jsonify({'success': False, 'message': 'New password must be at least 6 characters long.'}), 400
            
        if new_pwd != confirm_pwd:
            return jsonify({'success': False, 'message': 'New passwords do not match.'}), 400
            
        current_user.set_password(new_pwd)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Password changed successfully!'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
