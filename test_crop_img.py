import json
from PIL import Image

def process_image(img_path, box_2d, output_path):
    img = Image.open(img_path)
    w, h = img.size
    
    # box_2d is [ymin, xmin, ymax, xmax] mapping to 0-1000
    ymin, xmin, ymax, xmax = box_2d
    
    left = int(xmin * w / 1000)
    top = int(ymin * h / 1000)
    right = int(xmax * w / 1000)
    bottom = int(ymax * h / 1000)
    
    cropped = img.crop((left, top, right, bottom))
    cropped.save(output_path)
    print(f"Saved cropped to {output_path}")

try:
    process_image(
        "C:/Users/ASUS/.gemini/antigravity/brain/0cbe73bb-e701-4f4c-8634-c279e8637703/media__1775031413757.jpg",
        [217, 268, 878, 732],
        "test_crop.jpg"
    )
except Exception as e:
    print(e)
