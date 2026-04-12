import os
import io
import asyncio
from PIL import Image
from google import genai
from google.genai import types

from dotenv import load_dotenv
load_dotenv(".env")
api_key = os.getenv("GEMINI_API_KEY")

async def main():
    client = genai.Client(api_key=api_key)
    try:
        img = Image.open("C:/Users/ASUS/.gemini/antigravity/brain/0cbe73bb-e701-4f4c-8634-c279e8637703/media__1775031779951.png")
    except Exception as e:
        print(f"Error opening image: {e}")
        return
        
    prompt = """Analyze this document image. We are going to crop out the diagram/photo using your coordinates. 
    1. Identify the bounding box of the diagram/photo ONLY. 
    2. LOOK CLOSELY at the top boundary (ymin) of your box. Does it intersect with or include ANY text characters or sentences above the engine? If yes, you must increase the `ymin` value significantly to push the top boundary DOWN until it touches ONLY the metal parts of the engine. Wait, it must not touch any text!
    3. Ensure no text is located inside the box [ymin, xmin, ymax, xmax] (0-1000 scale).
    Return JSON format:
    {
      "diagrams": [ {"box_2d": [ymin, xmin, ymax, xmax]} ]
    }
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[img, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )
    print("Coordinates:", response.text)

asyncio.run(main())
