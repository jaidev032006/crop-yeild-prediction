import unittest
import json
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Admin, Product, Prediction, Order, Feedback
from app.services.ml_service import MLService
from app.services.pdf_service import PDFReportService

class AgriSmartTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed Test User
        self.user = User(
            username='testfarmer',
            email='farmer@test.com',
            first_name='Test',
            last_name='Farmer',
            location='Pune',
            phone='+91 99999 88888'
        )
        self.user.set_password('testpass123')
        db.session.add(self.user)

        # Seed Test Admin
        self.admin = Admin(
            username='testadmin',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            force_change_password=True
        )
        self.admin.set_password('adminpass123')
        db.session.add(self.admin)

        # Seed Test Product
        self.product = Product(
            name='Test Seeds',
            description='Certified high-yield seeds',
            category='Seeds',
            price=250.0,
            stock=50,
            image_url='https://example.com/seed.jpg'
        )
        db.session.add(self.product)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_landing_page(self):
        """Test landing page loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AgriSmart', response.data)

    def test_ml_service_prediction(self):
        """Test ML Service prediction and yield calculation"""
        res = MLService.predict(90, 42, 43, 24.0, 82.0, 6.5, 235.0)
        self.assertIn('crop', res)
        self.assertIn('confidence', res)
        self.assertIn('yield_estimate', res)
        self.assertIn('fertilizer_recommendation', res)
        self.assertEqual(res['crop'], 'Rice')
        self.assertGreater(res['yield_estimate'], 0)

    def test_user_login_and_predict_flow(self):
        """Test user login, prediction API submission, and PDF download"""
        # Login
        login_res = self.client.post('/auth/login', data={
            'username_or_email': 'testfarmer',
            'password': 'testpass123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)

        # API Predict
        pred_res = self.client.post('/predict/api/predict', json={
            'n': 70, 'p': 42, 'k': 20,
            'temp': 23.0, 'humid': 65.0, 'ph': 6.2, 'rain': 110.0
        })
        self.assertEqual(pred_res.status_code, 200)
        pred_data = json.loads(pred_res.data)
        self.assertTrue(pred_data['success'])
        self.assertEqual(pred_data['crop'], 'Maize')
        prediction_id = pred_data['prediction_id']

        # Download PDF Report
        report_res = self.client.get(f'/predict/report/{prediction_id}')
        self.assertEqual(report_res.status_code, 200)
        self.assertEqual(report_res.mimetype, 'application/pdf')

    def test_marketplace_checkout_and_orders(self):
        """Test marketplace cart checkout, order creation, and order listing"""
        # Login
        self.client.post('/auth/login', data={
            'username_or_email': 'testfarmer',
            'password': 'testpass123'
        })

        checkout_res = self.client.post('/marketplace/api/checkout', json={
            'items': [{'id': self.product.id, 'quantity': 2}],
            'shipping': {'name': 'Test Farmer', 'address': 'Farm 1', 'city': 'Pune', 'phone': '9999988888'},
            'payment': {'method': 'Credit Card'}
        })
        self.assertEqual(checkout_res.status_code, 200)
        checkout_data = json.loads(checkout_res.data)
        self.assertTrue(checkout_data['success'])
        self.assertEqual(checkout_data['total_amount'], 500.0)

        # Verify stock reduced
        updated_prod = Product.query.get(self.product.id)
        self.assertEqual(updated_prod.stock, 48)

        # Verify order appears in orders page
        orders_page = self.client.get('/marketplace/orders')
        self.assertEqual(orders_page.status_code, 200)
        self.assertIn(checkout_data['order_number'].encode(), orders_page.data)

    def test_feedback_submission(self):
        """Test farmer feedback submission API"""
        self.client.post('/auth/login', data={
            'username_or_email': 'testfarmer',
            'password': 'testpass123'
        })

        fb_res = self.client.post('/feedback/api/submit', json={
            'rating': 5,
            'message': 'Outstanding crop recommendations!',
            'is_public': True
        })
        self.assertEqual(fb_res.status_code, 200)
        fb_data = json.loads(fb_res.data)
        self.assertTrue(fb_data['success'])
        self.assertEqual(Feedback.query.count(), 1)

    def test_free_delivery_threshold(self):
        """Test free delivery logic (>= ₹500 is free, < ₹500 adds ₹50 delivery fee)"""
        self.client.post('/auth/login', data={
            'username_or_email': 'testfarmer',
            'password': 'testpass123'
        })

        # Subtotal 250 (1 item) -> Delivery fee = 50.0, Total = 300.0
        res_below = self.client.post('/marketplace/api/checkout', json={
            'items': [{'id': self.product.id, 'quantity': 1}],
            'shipping': {'name': 'Test Farmer', 'address': 'Farm 1', 'city': 'Pune', 'phone': '9999988888'},
            'payment': {'method': 'UPI (Google Pay / PhonePe)'}
        })
        data_below = json.loads(res_below.data)
        self.assertEqual(data_below['delivery_fee'], 50.0)
        self.assertEqual(data_below['total_amount'], 300.0)

        # Subtotal 500 (2 items) -> Delivery fee = 0.0 (FREE Delivery), Total = 500.0
        res_above = self.client.post('/marketplace/api/checkout', json={
            'items': [{'id': self.product.id, 'quantity': 2}],
            'shipping': {'name': 'Test Farmer', 'address': 'Farm 1', 'city': 'Pune', 'phone': '9999988888'},
            'payment': {'method': 'Credit/Debit Card'}
        })
        data_above = json.loads(res_above.data)
        self.assertEqual(data_above['delivery_fee'], 0.0)
        self.assertEqual(data_above['total_amount'], 500.0)

    def test_admin_control_room_flow(self):
        """Test admin login, password update, order status change, and CSV export"""
        # Admin Login
        admin_login = self.client.post('/admin/login', data={
            'username': 'testadmin',
            'password': 'adminpass123'
        }, follow_redirects=True)
        self.assertEqual(admin_login.status_code, 200)
        self.assertIn(b'CONTROL ROOM', admin_login.data)

        # Admin Export Orders CSV
        orders_csv = self.client.get('/admin/api/export-orders')
        self.assertEqual(orders_csv.status_code, 200)
        self.assertEqual(orders_csv.mimetype, 'text/csv')

        # Admin Export Predictions CSV
        csv_res = self.client.get('/admin/api/export-predictions')
        self.assertEqual(csv_res.status_code, 200)
        self.assertEqual(csv_res.mimetype, 'text/csv')

if __name__ == '__main__':
    unittest.main()
