import os
import sys
from app import create_app, db
from app.models import Product

def add_products():
    app = create_app()
    with app.app_context():
        print("[*] Adding more products to AgriSmart Database...")
        
        new_products = [
            # Seeds
            Product(
                name='High-Yield Wheat Seeds (Sharbati)',
                description='Premium quality, drought-resistant Sharbati wheat seeds ensuring long grains and high nutritional value.',
                category='Seeds',
                price=850.00,
                stock=50,
                image_url='/static/images/products/wheat_seeds.jpg',
                rating=4.7,
                is_active=True
            ),
            Product(
                name='Organic Tomato Seeds (Heirloom)',
                description='Certified organic, non-GMO heirloom tomato seeds perfect for greenhouse and open field cultivation.',
                category='Seeds',
                price=120.00,
                stock=300,
                image_url='/static/images/products/organic_tomato_seeds.jpg',
                rating=4.9,
                is_active=True
            ),
            # Fertilizer
            Product(
                name='Liquid NPK (19:19:19) Water Soluble',
                description='100% water-soluble NPK fertilizer for foliar application and drip fertigation. Promotes balanced growth.',
                category='Fertilizer',
                price=450.00,
                stock=80,
                image_url='/static/images/products/liquid_npk_fertilizer.jpg',
                rating=4.6,
                is_active=True
            ),
            Product(
                name='Zinc Sulphate Monohydrate (33%)',
                description='Crucial micronutrient fertilizer for correcting zinc deficiency, promoting chlorophyll synthesis and internode elongation.',
                category='Fertilizer',
                price=220.00,
                stock=150,
                image_url='/static/images/products/zinc_sulphate_fertilizer.jpg',
                rating=4.5,
                is_active=True
            ),
            # Tools
            Product(
                name='Ergonomic Soil Tiller & Cultivator',
                description='Heavy-duty hand tiller with carbon steel tines and ergonomic grip for breaking up compacted soil.',
                category='Tools',
                price=650.00,
                stock=40,
                image_url='/static/images/products/soil_tiller_cultivator.jpg',
                rating=4.8,
                is_active=True
            ),
            Product(
                name='Heavy Duty Pruning Shears',
                description='Professional grade pruning shears with titanium coated SK5 steel blades for clean cuts.',
                category='Tools',
                price=890.00,
                stock=60,
                image_url='/static/images/products/pruning_shears.jpg',
                rating=4.9,
                is_active=True
            ),
            # Organic
            Product(
                name='Neem Oil Bio-Pesticide (1L)',
                description='Cold-pressed, 100% pure neem oil extract. Highly effective natural pest control against aphids, mites, and whiteflies.',
                category='Organic',
                price=550.00,
                stock=100,
                image_url='/static/images/products/neem_oil_pesticide.jpg',
                rating=4.8,
                is_active=True
            ),
            Product(
                name='Seaweed Extract Plant Growth Promoter',
                description='Organic bio-stimulant derived from Ascophyllum Nodosum. Enhances root development and stress tolerance.',
                category='Organic',
                price=420.00,
                stock=120,
                image_url='/static/images/products/seaweed_extract_promoter.jpg',
                rating=4.7,
                is_active=True
            ),
            # Needs / General
            Product(
                name='Drip Irrigation Starter Kit (50m)',
                description='Complete DIY drip irrigation kit for small farms and kitchen gardens. Conserves water and boosts yield.',
                category='Tools',
                price=1850.00,
                stock=20,
                image_url='/static/images/products/drip_irrigation_kit.jpg',
                rating=4.5,
                is_active=True
            ),
            Product(
                name='UV-Stabilized Shade Net (50%, 10x10m)',
                description='Durable agro shade net providing 50% sun blockage. Protects crops from excessive heat and hail.',
                category='Tools',
                price=2400.00,
                stock=15,
                image_url='/static/images/products/shade_net_green.jpg',
                rating=4.6,
                is_active=True
            )
        ]
        
        db.session.add_all(new_products)
        db.session.commit()
        print(f"[+] Added {len(new_products)} new products to the database.")

if __name__ == '__main__':
    add_products()
