import os
from app import create_app, db
from app.models import Product

def update_unique_images():
    app = create_app()
    with app.app_context():
        print("[*] Updating specific products with their unique premium photos...")
        
        updates = {
            'Basmati Paddy Seeds (Super-1121)': '/static/images/products/basmati_paddy_seeds.jpg',
            'Hybrid Sweet Corn Maize Seeds': '/static/images/products/sweet_corn_seeds.jpg',
            'Organic Nitrogen Booster (Neem Coated Urea)': '/static/images/products/nitrogen_booster.jpg',
            'Diammonium Phosphate (DAP Granules)': '/static/images/products/dap_granules.jpg',
            'Muriate of Potash (MOP 60%)': '/static/images/products/mop_potash.jpg',
            'Smart Soil NPK & pH Digital Meter': '/static/images/products/smart_soil_meter.jpg',
            'High-Pressure Battery Backpack Sprayer (16L)': '/static/images/products/backpack_sprayer.jpg',
            'High-Yield Wheat Seeds (Sharbati)': '/static/images/products/wheat_seeds.jpg'
        }
        
        count = 0
        for name, img_url in updates.items():
            # Using like or exact match depending on the exact name in DB
            prod = Product.query.filter(Product.name.like(f"%{name}%")).first()
            if prod:
                prod.image_url = img_url
                count += 1
                
        db.session.commit()
        print(f"[+] Successfully applied unique images to {count} products.")

if __name__ == '__main__':
    update_unique_images()
