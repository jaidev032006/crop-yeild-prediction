from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Feedback

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/')
@login_required
def index():
    """Feedback page with animated stars and community testimonials"""
    public_feedback = Feedback.query.filter_by(is_public=True).order_by(Feedback.created_at.desc()).limit(12).all()
    user_feedbacks = Feedback.query.filter_by(user_id=current_user.id).order_by(Feedback.created_at.desc()).all()
    
    return render_template(
        'feedback/index.html',
        public_feedback=public_feedback,
        user_feedbacks=user_feedbacks
    )

@feedback_bp.route('/api/submit', methods=['POST'])
@login_required
def submit_feedback():
    """Submits user feedback"""
    try:
        data = request.get_json() or {}
        rating = int(data.get('rating', 5))
        message = data.get('message', '').strip()
        is_public = bool(data.get('is_public', True))
        
        if not message:
            return jsonify({'success': False, 'message': 'Please enter your feedback message.'}), 400
            
        if rating < 1 or rating > 5:
            rating = 5
            
        fb = Feedback(
            user_id=current_user.id,
            rating=rating,
            message=message,
            is_public=is_public
        )
        db.session.add(fb)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Thank you! Your feedback helps us build a smarter agricultural ecosystem.',
            'feedback': fb.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
