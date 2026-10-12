#!/usr/bin/env python
"""Seed database with default admin, sample farmers, marketplace products, and historical data"""

import os
import sys
from app import create_app, db
from app.models import Admin, User, Product, Prediction, Feedback, Order, OrderItem
from datetime import datetime, timedelta

def seed_database():
    app = create_app()
    
    with app.app_context():
        print("[*] Seeding AgriSmart Database...")
        db.create_all()

        # 1. Seed Admin
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(
                username='admin',
                email='admin@agrismart.com',
                first_name='Master',
                last_name='Operator',
                is_active=True,
                force_change_password=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("[+] Admin created: admin / admin123 (Force reset enabled)")
        else:
            print("[-] Admin already exists.")

        # 2. Seed Demo Farmer User
        user = User.query.filter_by(username='farmer_ravi').first()
        if not user:
            user = User(
                username='farmer_ravi',
                email='ravi.kumar@agrifarm.in',
                first_name='Ravi',
                last_name='Kumar',
                phone='+91 98765 43210',
                location='Pune, Maharashtra',
                bio='Cultivating paddy, wheat, and seasonal vegetables across 15 acres of loamy soil.',
                avatar_url='https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80',
                is_active=True
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            print("[+] Demo User created: farmer_ravi / password123")
        else:
            print("[-] Demo user already exists.")

        # 3. Seed Marketplace Products
        if Product.query.count() == 0:
            sample_products = [
                Product(
                    name='Basmati Paddy Seeds (Super-1121)',
                    description='Certified high-germination premium Basmati seeds with high disease resistance and long grain yield.',
                    category='Seeds',
                    price=550.00,
                    stock=120,
                    image_url='/static/images/products/basmati_paddy_seeds.jpg',
                    rating=4.9,
                    is_active=True
                ),
                Product(
                    name='Hybrid Sweet Corn Maize Seeds',
                    description='High yielding hybrid maize seeds suitable for Kharif & Spring seasons with drought tolerance.',
                    category='Seeds',
                    price=420.00,
                    stock=85,
                    image_url='/static/images/products/sweet_corn_seeds.jpg',
                    rating=4.8,
                    is_active=True
                ),
                Product(
                    name='Organic Nitrogen Booster (Neem Coated Urea)',
                    description='Slow-release nitrogen enrichment fertilizer with bio-active neem extract for soil microbes.',
                    category='Fertilizer',
                    price=380.00,
                    stock=150,
                    image_url='/static/images/products/nitrogen_booster.jpg',
                    rating=4.9,
                    is_active=True
                ),
                Product(
                    name='Diammonium Phosphate (DAP Granules)',
                    description='High-grade phosphate & root zone stimulant suitable for initial vegetative development.',
                    category='Fertilizer',
                    price=750.00,
                    stock=90,
                    image_url='/static/images/products/dap_granules.jpg',
                    rating=4.7,
                    is_active=True
                ),
                Product(
                    name='Muriate of Potash (MOP 60%)',
                    description='Premium potassium chloride granules for enhancing drought resilience and fruit weight.',
                    category='Fertilizer',
                    price=620.00,
                    stock=110,
                    image_url='/static/images/products/mop_potash.jpg',
                    rating=4.8,
                    is_active=True
                ),
                Product(
                    name='Smart Soil NPK & pH Digital Meter',
                    description='Rapid 4-in-1 digital soil probe for instant on-field telemetry of moisture, pH, and nutrient indices.',
                    category='Tools',
                    price=2800.00,
                    stock=25,
                    image_url='/static/images/products/smart_soil_meter.jpg',
                    rating=4.9,
                    is_active=True
                ),
                Product(
                    name='High-Pressure Battery Backpack Sprayer (16L)',
                    description='Cordless electric sprayer with dual pressure nozzles for foliar spray and bio-pesticides.',
                    category='Tools',
                    price=3450.00,
                    stock=18,
                    image_url='/static/images/products/backpack_sprayer.jpg',
                    rating=4.8,
                    is_active=True
                ),
                Product(
                    name='Organic Vermicompost Enricher (25kg)',
                    description='100% pure worm castings loaded with humic acid, beneficial fungi, and micronutrients.',
                    category='Organic',
                    price=490.00,
                    stock=200,
                    image_url='/static/images/products/vermicompost_enricher.jpg',
                    rating=5.0,
                    is_active=True
                )
            ]
            db.session.add_all(sample_products)
            db.session.commit()
            print(f"[+] {len(sample_products)} Marketplace Products seeded.")

        # 4. Seed Historical Predictions for Demo User
        if Prediction.query.filter_by(user_id=user.id).count() == 0:
            preds = [
                Prediction(
                    user_id=user.id,
                    nitrogen=90, phosphorus=42, potassium=43,
                    temperature=24.0, humidity=82.0, ph=6.5, rainfall=235.0,
                    predicted_crop='Rice', confidence=98.6,
                    yield_estimate=4.2, yield_efficiency=88.5,
                    fertilizer_recommendation="• Nitrogen (N) is OPTIMAL for this crop.\n• Phosphorus (P) is OPTIMAL for this crop.\n• Potassium (K) is OPTIMAL for this crop.",
                    created_at=datetime.utcnow() - timedelta(days=2)
                ),
                Prediction(
                    user_id=user.id,
                    nitrogen=70, phosphorus=42, potassium=20,
                    temperature=23.0, humidity=65.0, ph=6.2, rainfall=110.0,
                    predicted_crop='Maize', confidence=97.4,
                    yield_estimate=4.6, yield_efficiency=92.0,
                    fertilizer_recommendation="• Nitrogen (N) is OPTIMAL for this crop.\n• Phosphorus (P) is OPTIMAL for this crop.\n• Potassium (K) is OPTIMAL for this crop.",
                    created_at=datetime.utcnow() - timedelta(days=5)
                )
            ]
            db.session.add_all(preds)
            db.session.commit()
            print("[+] Sample prediction records seeded.")

        # 5. Seed Sample Orders
        if Order.query.filter_by(user_id=user.id).count() == 0:
            first_prod = Product.query.first()
            if first_prod:
                order = Order(
                    user_id=user.id,
                    order_number="AGR-2409-P4289",
                    status="Shipped",
                    total_amount=first_prod.price * 2,
                    shipping_name=user.display_name,
                    shipping_address="Plot 42, Green Fields Road",
                    shipping_city=user.location,
                    shipping_phone=user.phone,
                    payment_method="Credit Card",
                    payment_status="Paid",
                    created_at=datetime.utcnow() - timedelta(days=1)
                )
                db.session.add(order)
                db.session.flush()

                item = OrderItem(
                    order_id=order.id,
                    product_id=first_prod.id,
                    quantity=2,
                    unit_price=first_prod.price
                )
                db.session.add(item)
                db.session.commit()
                print("[+] Sample order created.")

        # 6. Seed Community Feedback
        if Feedback.query.count() == 0:
            feedbacks = [
                Feedback(
                    user_id=user.id,
                    rating=5,
                    message="The AI fertilizer recommendations were spot on! Applying the suggested DAP split increased our Basmati grain weight significantly.",
                    is_public=True,
                    created_at=datetime.utcnow() - timedelta(days=3)
                ),
                Feedback(
                    user_id=user.id,
                    rating=5,
                    message="The Open-Meteo live rainfall sync made planning irrigation effortless. The PDF report helped us get formal bank micro-credit approval.",
                    is_public=True,
                    created_at=datetime.utcnow() - timedelta(days=7)
                )
            ]
            db.session.add_all(feedbacks)
            db.session.commit()
            print("[+] Community feedback seeded.")

        print("\n[SUCCESS] Database initialization & seeding completed successfully!")

if __name__ == '__main__':
    seed_database()
