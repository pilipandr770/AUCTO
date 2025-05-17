# scripts/png_to_svg.py
"""
Скрипт перетворює PNG-логотип (assets/logo.png)
у SVG 32×32 з вбудованим зображенням.
"""
from PIL import Image
import base64, io, os

# Тепер cwd — це C:\Users\ПК\aucto777\app
project_root = os.getcwd()
input_path  = os.path.join(project_root, 'assets', 'logo.png')
output_path = os.path.join(project_root, 'assets', 'logo.svg')

# Завантаження та resize
img = Image.open(input_path).convert("RGBA")
img = img.resize((32, 32), Image.LANCZOS)

# Кодування в Base64
buffer = io.BytesIO()
img.save(buffer, format="PNG")
b64_data = base64.b64encode(buffer.getvalue()).decode('ascii')

# Формування SVG
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32">
<image href="data:image/png;base64,{b64_data}" width="32" height="32"/>
</svg>
'''

# Запис у файл
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(svg)

print(f'SVG збережено: {output_path}')
