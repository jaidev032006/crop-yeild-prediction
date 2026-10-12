import os
import sys
from app import create_app, db
from app.models import Product

def add_more_products():
    app = create_app()
    with app.app_context():
        print("[*] Adding even more products to AgriSmart Database...")
        
        new_products = [
            # Seeds
            Product(
                name='Sunflower Seeds (High Oil Yield)',
                description='Premium hybrid sunflower seeds bred for high oil content and disease resistance.',
                category='Seeds',
                price=340.00,
                stock=150,
                image_url='/static/images/products/sunflower_seeds.jpg',
                rating=4.5,
                is_active=True
            ),
            Product(
                name='Cotton Seeds (Bt Hybrid)',
                description='High-yielding Bt cotton seeds with built-in resistance to bollworm complex.',
                category='Seeds',
                price=950.00,
                stock=200,
                image_url='/static/images/products/cotton_seeds.jpg',
                rating=4.8,
                is_active=True
            ),
            Product(
                name='Soybean Seeds (Yellow, 5kg)',
                description='High germination yellow soybean seeds suitable for both Kharif and Rabi seasons.',
                category='Seeds',
                price=620.00,
                stock=100,
                image_url='/static/images/products/soybean_seeds.jpg',
                rating=4.6,
                is_active=True
            ),
            
            # Fertilizer
            Product(
                name='Calcium Nitrate (100% Water Soluble)',
                description='Provides fast-acting calcium and nitrate-nitrogen to prevent blossom end rot and improve cell wall strength.',
                category='Fertilizer',
                price=520.00,
                stock=80,
                image_url='/static/images/products/calcium_nitrate.jpg',
                rating=4.7,
                is_active=True
            ),
            Product(
                name='Bone Meal Fertilizer (5kg)',
                description='Excellent slow-release source of phosphorus and calcium for strong root development and abundant flowering.',
                category='Fertilizer',
                price=350.00,
                stock=120,
                image_url='/static/images/products/bone_meal_fertilizer.jpg',
                rating=4.4,
                is_active=True
            ),
            
            # Tools & Equipment
            Product(
                name='Heavy-Duty Wheelbarrow (80L)',
                description='Pneumatic tire wheelbarrow with a rust-resistant galvanized steel tray for heavy farm loads.',
                category='Tools',
                price=4500.00,
                stock=10,
                image_url='/static/images/products/heavy_duty_wheelbarrow.jpg',
                rating=4.9,
                is_active=True
            ),
            Product(
                name='Agro Weather Station (Solar Powered)',
                description='Compact on-field weather station measuring wind, rain, temperature, and humidity with Bluetooth sync.',
                category='Tools',
                price=8500.00,
                stock=5,
                image_url='/static/images/products/agro_weather_station.jpg',
                rating=5.0,
                is_active=True
            ),
            Product(
                name='Farmer Protective Gear Set',
                description='Includes a broad-brimmed hat, UV-protection sleeves, safety goggles, and heavy-duty nitrile gloves.',
                category='Tools',
                price=1250.00,
                stock=45,
                image_url='/static/images/products/farmer_protective_gear.jpg',
                rating=4.8,
                is_active=True
            ),
            Product(
                name='Digital Seed Sowing Machine (Manual Push)',
                description='Precision push-type seeder for accurate spacing and depth control for corn, beans, and peanuts.',
                category='Tools',
                price=3200.00,
                stock=12,
                image_url='/static/images/products/digital_seed_sowing_machine.jpg',
                rating=4.6,
                is_active=True
            ),
            
            # Organic & Bio
            Product(
                name='Trichoderma Viride Bio-Fungicide (1kg)',
                description='Eco-friendly bio-fungicide that protects roots from soil-borne diseases like wilt and root rot.',
                category='Organic',
                price=280.00,
                stock=90,
                image_url='/static/images/products/trichoderma_viride.jpg',
                rating=4.7,
                is_active=True
            ),
            Product(
                name='Pseudomonas Fluorescens Bio-Bactericide',
                description='Beneficial bacteria that suppress plant diseases and promote systemic resistance in crops.',
                category='Organic',
                price=310.00,
                stock=75,
                image_url='/static/images/products/pseudomonas_fluorescens.jpg',
                rating=4.5,
                is_active=True
            ),
            Product(
                name='Organic Coconut Coir Bricks (Pack of 5)',
                description='Expands in water to create a perfect, aerated growing medium. 100% natural and peat-free.',
                category='Organic',
                price=490.00,
                stock=200,
                image_url='/static/images/products/coconut_coir_bricks.jpg',
                rating=4.9,
                is_active=True
            ),
            
            # Needs / General
            Product(
                name='Mulching Film (Silver/Black, 400m)',
                description='High-quality UV-stabilized mulching paper to prevent weed growth and conserve soil moisture.',
                category='Tools',
                price=1750.00,
                stock=25,
                image_url='/static/images/products/mulching_film.jpg',
                rating=4.7,
                is_active=True
            ),
            Product(
                name='Fruit Fly Pheromone Traps (Pack of 10)',
                description='Non-toxic, highly effective pheromone lures and traps to protect orchards and vegetable crops.',
                category='Organic',
                price=850.00,
                stock=60,
                image_url='/static/images/products/fruit_fly_pheromone_traps.jpg',
                rating=4.8,
                is_active=True
            )
        ]
        
        db.session.add_all(new_products)
        db.session.commit()
        print(f"[+] Added {len(new_products)} more products to the database.")

if __name__ == '__main__':
    add_more_products()
