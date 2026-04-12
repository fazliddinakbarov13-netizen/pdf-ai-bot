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
        
    prompt = """Analyze this document image. We are reconstructing the layout.
    1. Extract the text completely.
    2. Identify the `bottom_y_coordinate_of_all_text` (0-1000 scale). This is the exact Y-coordinate where the LAST line of text ends.
    3. Identify the bounding boxes of ONLY the non-text pure graphical elements. The `ymin` of the diagram MUST be greater than `bottom_y_coordinate_of_all_text`.
    Return ONLY valid JSON exactly like this:
    {
      "text": "...",
      "bottom_y_coordinate_of_all_text": 250,
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
    print("Result:", response.text)

asyncio.run(main())
