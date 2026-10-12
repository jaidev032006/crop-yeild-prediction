import json
import urllib.request
import urllib.parse
import time
from app import create_app, db
from app.models import Product

mapping = {
    26: "Personal protective equipment",
    27: "Seed drill",
    28: "Fungicide",
    29: "Pseudomonas fluorescens",
    30: "Coir",
    31: "Plastic mulch",
    32: "Pheromone trap"
}

def get_exact_wiki_image(title):
    encoded = urllib.parse.quote(title)
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={encoded}&prop=pageimages&pithumbsize=800&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'AgriSmart/1.1 (Contact: jaivi@example.com)'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            pages = data.get('query', {}).get('pages', {})
            for page_id in pages:
                if 'thumbnail' in pages[page_id]:
                    return pages[page_id]['thumbnail']['source']
    except Exception as e:
        print(f"Error for {title}: {e}")
    return None

def fix_images():
    app = create_app()
    with app.app_context():
        count = 0
        for pid, title in mapping.items():
            p = db.session.get(Product, pid)
            if p:
                img = get_exact_wiki_image(title)
                if img:
                    p.image_url = img
                    count += 1
                    print(f"[OK] Updated {p.name} -> {img}")
                else:
                    print(f"[FAIL] Could not find exact image for {title}")
            time.sleep(2)
        db.session.commit()
        print(f"Updated {count} products.")

if __name__ == '__main__':
    fix_images()
