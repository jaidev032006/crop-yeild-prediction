from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    # Support loading both User and Admin if needed, or by prefix/model
    if str(user_id).startswith('admin_'):
        admin_id = int(str(user_id).replace('admin_', ''))
        return Admin.query.get(admin_id)
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    """User model for farmers and regular users"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80), default='')
    last_name = db.Column(db.String(80), default='')
    avatar_url = db.Column(db.String(255), default='')
    phone = db.Column(db.String(20), default='')
    location = db.Column(db.String(255), default='India')
    bio = db.Column(db.Text, default='')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='user', lazy=True, cascade='all, delete-orphan', order_by='desc(Prediction.created_at)')
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan', order_by='desc(Order.created_at)')
    feedback_list = db.relationship('Feedback', backref='user', lazy=True, cascade='all, delete-orphan', order_by='desc(Feedback.created_at)')
    
    @property
    def display_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.first_name:
            return self.first_name
        return self.username

    @property
    def avatar(self):
        if self.avatar_url:
            return self.avatar_url
        name = self.display_name.replace(' ', '+')
        return f"https://ui-avatars.com/api/?name={name}&background=0f5132&color=fff&rounded=true&bold=true"
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'display_name': self.display_name,
            'phone': self.phone,
            'location': self.location,
            'bio': self.bio,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'predictions_count': len(self.predictions),
            'orders_count': len(self.orders)
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class Admin(UserMixin, db.Model):
    """Admin model for control room access"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80), default='Admin')
    last_name = db.Column(db.String(80), default='Operator')
    is_active = db.Column(db.Boolean, default=True)
    force_change_password = db.Column(db.Boolean, default=True)  # Force change on first login
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Prefix admin id to differentiate from user in session loader
    def get_id(self):
        return f"admin_{self.id}"

    @property
    def is_admin(self):
        return True

    @property
    def display_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Admin {self.username}>'

class Prediction(db.Model):
    """Crop prediction history"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Input parameters
    nitrogen = db.Column(db.Float, nullable=False)
    phosphorus = db.Column(db.Float, nullable=False)
    potassium = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    ph = db.Column(db.Float, nullable=False)
    rainfall = db.Column(db.Float, nullable=False)
    
    # Prediction results
    predicted_crop = db.Column(db.String(100), nullable=False)
    confidence = db.Column(db.Float, default=98.6)  # Model accuracy %
    yield_estimate = db.Column(db.Float, default=4.0)  # tons/hectare
    yield_efficiency = db.Column(db.Float, default=85.0)  # efficiency %
    fertilizer_recommendation = db.Column(db.Text)
    location = db.Column(db.String(150), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'location': self.location or 'General Field',
            'nitrogen': self.nitrogen,
            'phosphorus': self.phosphorus,
            'potassium': self.potassium,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'ph': self.ph,
            'rainfall': self.rainfall,
            'predicted_crop': self.predicted_crop,
            'confidence': self.confidence,
            'yield_estimate': self.yield_estimate,
            'yield_efficiency': self.yield_efficiency,
            'fertilizer_recommendation': self.fertilizer_recommendation,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'date_formatted': self.created_at.strftime('%b %d, %Y - %I:%M %p')
        }

    def __repr__(self):
        return f'<Prediction {self.predicted_crop} - {self.created_at}>'

class Product(db.Model):
    """Marketplace products (crops, seeds, fertilizers, tools)"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), default='Seeds')  # Seeds, Fertilizer, Tools, Organic
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=50)
    image_url = db.Column(db.String(255))
    rating = db.Column(db.Float, default=4.8)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': self.price,
            'stock': self.stock,
            'image_url': self.image_url or f"https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400&auto=format&fit=crop&q=60",
            'rating': self.rating,
            'is_active': self.is_active
        }

    def __repr__(self):
        return f'<Product {self.name}>'

class Order(db.Model):
    """Marketplace orders"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.String(50), default='Pending')  # Pending, Confirmed, Shipped, Delivered, Cancelled
    total_amount = db.Column(db.Float, default=0.0)
    
    shipping_name = db.Column(db.String(120), default='')
    shipping_address = db.Column(db.String(255), default='')
    shipping_city = db.Column(db.String(100), default='')
    shipping_phone = db.Column(db.String(30), default='')
    payment_method = db.Column(db.String(50), default='Credit/Debit Card')
    payment_status = db.Column(db.String(50), default='Paid')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    @property
    def status_step(self):
        steps = {'Pending': 1, 'Confirmed': 2, 'Shipped': 3, 'Delivered': 4, 'Cancelled': 0}
        return steps.get(self.status, 1)

    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'status': self.status,
            'status_step': self.status_step,
            'total_amount': round(self.total_amount, 2),
            'shipping_name': self.shipping_name,
            'shipping_address': self.shipping_address,
            'shipping_city': self.shipping_city,
            'shipping_phone': self.shipping_phone,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'date_formatted': self.created_at.strftime('%B %d, %Y'),
            'items': [item.to_dict() for item in self.items]
        }

    def __repr__(self):
        return f'<Order {self.order_number}>'

class OrderItem(db.Model):
    """Individual items in an order"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    
    # Relationship
    product = db.relationship('Product', backref='order_items')
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Unknown Product',
            'product_image': self.product.image_url if self.product else '',
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'subtotal': round(self.quantity * self.unit_price, 2)
        }

    def __repr__(self):
        return f'<OrderItem {self.product.name if self.product else self.product_id} x{self.quantity}>'

class Feedback(db.Model):
    """User feedback and ratings"""
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    rating = db.Column(db.Integer, default=5)  # 1-5 stars
    message = db.Column(db.Text, nullable=False)
    is_public = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.display_name if self.user else 'Anonymous Farmer',
            'avatar': self.user.avatar if self.user else '',
            'location': self.user.location if self.user else '',
            'rating': self.rating,
            'message': self.message,
            'is_public': self.is_public,
            'created_at': self.created_at.strftime('%b %d, %Y')
        }

    def __repr__(self):
        return f'<Feedback {self.user_id} - {self.rating}★>'
