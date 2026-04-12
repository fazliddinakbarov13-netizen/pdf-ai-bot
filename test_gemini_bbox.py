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
        
    prompt = """Analyze this document image.
    1. Extract all text completely.
    2. We need to reconstruct this document strictly separating text and graphics.
    3. Identify the bounding boxes of any non-text graphics, illustrations, or photos.
    Use the format [ymin, xmin, ymax, xmax] (0-1000).
    Return JSON format exactly like this:
    {
      "text": "full extracted text",
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
    print(response.text)

asyncio.run(main())
