from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
import os
import datetime

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access your AgriSmart dashboard.'
    login_manager.login_message_category = 'info'
    
    # Context Processors & Template Filters
    @app.context_processor
    def inject_globals():
        now = datetime.datetime.now()
        hour = now.hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
            
        return {
            'current_year': now.year,
            'time_greeting': greeting,
            'app_name': 'AgriSmart'
        }
    
    # Register blueprints
    with app.app_context():
        from app.routes.main import main_bp
        from app.routes.auth import auth_bp
        from app.routes.dashboard import dashboard_bp
        from app.routes.predict import predict_bp
        from app.routes.marketplace import marketplace_bp
        from app.routes.feedback import feedback_bp
        from app.routes.profile import profile_bp
        from app.routes.analytics import analytics_bp
        from app.routes.admin import admin_bp
        
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
        app.register_blueprint(predict_bp, url_prefix='/predict')
        app.register_blueprint(marketplace_bp, url_prefix='/marketplace')
        app.register_blueprint(feedback_bp, url_prefix='/feedback')
        app.register_blueprint(profile_bp, url_prefix='/profile')
        app.register_blueprint(analytics_bp, url_prefix='/analytics')
        app.register_blueprint(admin_bp, url_prefix='/admin')
        
        # Create database tables
        db.create_all()
    
    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.route('/sw.js')
    def kill_legacy_service_worker():
        from flask import Response
        js = """
self.addEventListener('install', () => {
    self.skipWaiting();
});
self.addEventListener('activate', () => {
    self.registration.unregister().then(() => {
        return self.clients.matchAll();
    }).then(clients => {
        clients.forEach(client => client.navigate(client.url));
    });
});
"""
        response = Response(js, mimetype='application/javascript')
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Clear-Site-Data'] = '"cache", "storage"'
        return response

    return app
