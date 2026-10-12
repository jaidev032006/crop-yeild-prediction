import json
import urllib.request
import urllib.parse
from app import create_app, db
from app.models import Product

def get_wiki_image(keyword):
    encoded = urllib.parse.quote(keyword)
    url = f"https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={encoded}&gsrlimit=1&prop=pageimages&pithumbsize=800&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'AgriSmart/1.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for page_id in pages:
                if 'thumbnail' in pages[page_id]:
                    return pages[page_id]['thumbnail']['source']
    except Exception as e:
        pass
    return None

def update_remaining_images():
    app = create_app()
    with app.app_context():
        print("[*] Fetching unique contextual images from Wikipedia for remaining products...")
        
        products = Product.query.all()
        count = 0
        
        for p in products:
            # If the image is generic or broken
            if 'generic' in p.image_url or 'unsplash' in p.image_url:
                # Clean up name for better search (e.g. "Sunflower Seeds (High Oil Yield)" -> "Sunflower")
                search_term = p.name.split('(')[0].split('-')[0].replace('Organic', '').replace('Premium', '').strip()
                if not search_term:
                    search_term = p.category
                
                print(f"  -> Searching for '{search_term}' (Product: {p.name})")
                img = get_wiki_image(search_term + " agriculture")
                if not img:
                    img = get_wiki_image(search_term)
                
                if img:
                    p.image_url = img
                    count += 1
                    print(f"     [OK] Found image: {img}")
                else:
                    # Absolute fallback to loremflickr if wiki fails, with specific keyword
                    fallback_keyword = urllib.parse.quote(search_term.split()[0])
                    # To prevent browser caching the same redirect, append a unique ID parameter
                    p.image_url = f"https://loremflickr.com/800/600/agriculture,{fallback_keyword}?lock={p.id}"
                    count += 1
                    print(f"     [Fallback] Used LoremFlickr for: {search_term}")
                    
        db.session.commit()
        print(f"[+] Successfully applied unique, distinct images to {count} remaining products.")

if __name__ == '__main__':
    update_remaining_images()
