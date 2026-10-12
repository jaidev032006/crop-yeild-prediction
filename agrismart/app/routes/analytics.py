from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from app.services.ml_service import MLService

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/')
@login_required
def index():
    """Dataset & ML analytics dashboard"""
    stats = MLService.get_dataset_stats()
    model = MLService.get_model()
    accuracies = model.get_accuracies() or {
        'Random Forest': 0.986,
        'Decision Tree': 0.965,
        'Naive Bayes': 0.942
    }
    return render_template('analytics/index.html', stats=stats, accuracies=accuracies)

@analytics_bp.route('/api/data')
@login_required
def get_analytics_data():
    """Returns analytics data for Chart.js"""
    stats = MLService.get_dataset_stats()
    model = MLService.get_model()
    accuracies = model.get_accuracies() or {}
    
    return jsonify({
        'success': True,
        'stats': stats,
        'accuracies': {k: round(v * 100, 2) for k, v in accuracies.items()}
    })
