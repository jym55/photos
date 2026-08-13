import os
import re
from PIL import Image

# Configuration des dossiers
MEDIAS_DIR = "medias"
THUMBS_DIR = "thumbnails"
INDEX_FILE = "index.html"
THUMB_MAX_HEIGHT = 600

VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG', '.PNG', '.WEBP')

os.makedirs(THUMBS_DIR, exist_ok=True)
os.makedirs(MEDIAS_DIR, exist_ok=True)

items = []

print("🔎 Analyse du dossier 'medias/'...")

files = sorted([f for f in os.listdir(MEDIAS_DIR) if f.endswith(VALID_EXTENSIONS)])

for filename in files:
    photo_path = os.path.join(MEDIAS_DIR, filename)
    thumb_path = os.path.join(THUMBS_DIR, filename)
    
    try:
        with Image.open(photo_path) as img:
            width, height = img.size
            
            # Génération de la vignette si inexistante
            if not os.path.exists(thumb_path):
                img_copy = img.copy()
                ratio = THUMB_MAX_HEIGHT / float(height)
                if ratio < 1.0:
                    new_width = int(float(width) * ratio)
                    img_copy = img_copy.resize((new_width, THUMB_MAX_HEIGHT), Image.Resampling.LANCZOS)
                
                if img_copy.mode in ("RGBA", "P"):
                    img_copy = img_copy.convert("RGB")
                    
                img_copy.save(thumb_path, quality=85, optimize=True)
                print(f"  ✓ Vignette créée : {filename}")

            title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()

            items.append({
                "src": f"medias/{filename}",
                "srct": f"thumbnails/{filename}",
                "title": title
            })

    except Exception as e:
        print(f"❌ Erreur sur {filename}: {e}")

# Formatting du tableau JavaScript
js_items = "items: [\n"
for item in items:
    js_items += f'        {{ src: "{item["src"]}", srct: "{item["srct"]}", title: "{item["title"]}" }},\n'
js_items += "      ]"

# Injection directe dans index.html
if os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remplacement du bloc items: [...] dans le fichier index.html
    updated_content = re.sub(r'items:\s*\[[\s\S]*?\]', js_items, content)
    
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        f.write(updated_content)
    
    print(f"\n✅ {len(items)} photo(s) injectée(s) directement dans {INDEX_FILE} !")
