import os
import sys
from app import create_app, db
from app.models import Product

def fix_images():
    app = create_app()
    with app.app_context():
        print("[*] Checking for products with missing or broken images...")
        
        products = Product.query.all()
        updated_count = 0
        
        for p in products:
            # If the image URL is empty, or contains unsplash (which are mostly broken now)
            if not p.image_url or 'unsplash' in p.image_url:
                if p.category == 'Seeds':
                    p.image_url = '/static/images/products/seeds_generic.jpg'
                elif p.category == 'Tools':
                    p.image_url = '/static/images/products/tools_generic.jpg'
                elif p.category == 'Fertilizer':
                    p.image_url = '/static/images/products/fertilizer_generic.jpg'
                elif p.category == 'Organic':
                    p.image_url = '/static/images/products/organic_generic.jpg'
                else:
                    p.image_url = '/static/images/products/tools_generic.jpg' # Default fallback
                updated_count += 1
                
        if updated_count > 0:
            db.session.commit()
            print(f"[+] Successfully fixed images for {updated_count} products.")
        else:
            print("[+] All product images are already set.")

if __name__ == '__main__':
    fix_images()
