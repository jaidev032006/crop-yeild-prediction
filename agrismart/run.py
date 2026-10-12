#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Admin, Prediction, Order, OrderItem, Product, Feedback

app = create_app(os.environ.get('FLASK_ENV', 'development'))

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Admin': Admin,
        'Prediction': Prediction,
        'Order': Order,
        'OrderItem': OrderItem,
        'Product': Product,
        'Feedback': Feedback
    }

@app.cli.command()
def init_db():
    """Initialize the database."""
    db.create_all()
    print("Database initialized.")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
