import os
import asyncio
import logging
import base64
from google import genai
from google.genai import types
from PIL import Image, ImageEnhance
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Zomro (Germany) serveri uchun Google V1 bloklangan. Shuning uchun proxy ishlatamiz.
base_url = os.getenv("GEMINI_BASE_URL", "https://gemini.chatxyz.online")

if base_url:
    client = genai.Client(api_key=api_key, http_options={'base_url': base_url})
else:
    client = genai.Client(api_key=api_key)

# Ovoz uchun to'g'ridan-to'g'ri API (proxy ba'zan ovozni qo'llab-quvvatlamaydi)
direct_client = genai.Client(api_key=api_key)

# ==================== OCR PROMPT ====================

STRUCTURED_OCR_PROMPT = """You are an expert document OCR system for official Uzbek documents.
Extract ALL text from this image completely and accurately. Do not skip any line or word.
This includes HANDWRITTEN text — carefully read and transcribe handwriting as well.

OUTPUT FORMAT RULES:
1. Each real paragraph = one continuous block of text (single long line). Do NOT break paragraphs into visual lines.
2. Separate paragraphs with exactly ONE empty line.
3. If a line is CENTERED (titles/headers), put [CENTER] before it on its own line.
4. If a paragraph has first-line indentation, put [INDENT] before it.
5. Do NOT use ** or any bold markers. Just output plain text.
6. Keep dash/bullet list items (- item) each on their own line with NO empty lines between consecutive dash items.
7. Do NOT add commentary, code blocks, or explanations.
8. Extract EVERY single word — do not skip or summarize anything.
9. FIX any obvious spelling and punctuation errors in the extracted text.

ALPHABET: Output MUST be in {alphabet}.
- 'Lotin' → O'zbek Latin
- 'Kirill' → O'zbek Cyrillic

Return ONLY the extracted text."""


# ==================== LOTIN <-> KIRILL KONVERTOR ====================

# O'zbek lotin -> kirill xaritasi
_LATIN_TO_CYRILLIC = {
    "yo'": "йў", "Yu": "Ю", "yu": "ю", "Ya": "Я", "ya": "я",
    "Yo": "Ё", "yo": "ё", "Ye": "Е", "ye": "е",
    "Sh": "Ш", "sh": "ш", "Ch": "Ч", "ch": "ч",
    "G'": "Ғ", "g'": "ғ", "O'": "Ў", "o'": "ў",
    "Ng": "Нг", "ng": "нг", "Ts": "Ц", "ts": "ц",
    "A": "А", "a": "а", "B": "Б", "b": "б",
    "D": "Д", "d": "д", "E": "Э", "e": "э",
    "F": "Ф", "f": "ф", "G": "Г", "g": "г",
    "H": "Ҳ", "h": "ҳ", "I": "И", "i": "и",
    "J": "Ж", "j": "ж", "K": "К", "k": "к",
    "L": "Л", "l": "л", "M": "М", "m": "м",
    "N": "Н", "n": "н", "O": "О", "o": "о",
    "P": "П", "p": "п", "Q": "Қ", "q": "қ",
    "R": "Р", "r": "р", "S": "С", "s": "с",
    "T": "Т", "t": "т", "U": "У", "u": "у",
    "V": "В", "v": "в", "X": "Х", "x": "х",
    "Y": "Й", "y": "й", "Z": "З", "z": "з",
    "'": "ъ",
}

# Kirill -> lotin xaritasi
_CYRILLIC_TO_LATIN = {
    "Ё": "Yo", "ё": "yo", "Ю": "Yu", "ю": "yu",
    "Я": "Ya", "я": "ya", "Ш": "Sh", "ш": "sh",
    "Ч": "Ch", "ч": "ch", "Ғ": "G'", "ғ": "g'",
    "Ў": "O'", "ў": "o'", "Ц": "Ts", "ц": "ts",
    "Щ": "Sh", "щ": "sh", "Ъ": "'", "ъ": "'",
    "Ь": "", "ь": "",
    "А": "A", "а": "a", "Б": "B", "б": "b",
    "В": "V", "в": "v", "Г": "G", "г": "g",
    "Д": "D", "д": "d", "Е": "E", "е": "e",
    "Ж": "J", "ж": "j", "З": "Z", "з": "z",
    "И": "I", "и": "i", "Й": "Y", "й": "y",
    "К": "K", "к": "k", "Қ": "Q", "қ": "q",
    "Л": "L", "л": "l", "М": "M", "м": "m",
    "Н": "N", "н": "n", "О": "O", "о": "o",
    "П": "P", "п": "p", "Р": "R", "р": "r",
    "С": "S", "с": "s", "Т": "T", "т": "t",
    "У": "U", "у": "u", "Ф": "F", "ф": "f",
    "Х": "X", "х": "x", "Ҳ": "H", "ҳ": "h",
}


def convert_latin_to_cyrillic(text: str) -> str:
    """Lotin yozuvini Kirill yozuviga o'girish."""
    result = text
    for lat, cyr in sorted(_LATIN_TO_CYRILLIC.items(), key=lambda x: -len(x[0])):
        result = result.replace(lat, cyr)
    return result


def convert_cyrillic_to_latin(text: str) -> str:
    """Kirill yozuvini Lotin yozuviga o'girish."""
    result = text
    for cyr, lat in sorted(_CYRILLIC_TO_LATIN.items(), key=lambda x: -len(x[0])):
        result = result.replace(cyr, lat)
    return result


def detect_script(text: str) -> str:
    """Matnning asosiy yozuvi qaysi ekanligini aniqlash."""
    cyrillic_count = 0
    latin_count = 0
    for ch in text:
        if '\u0400' <= ch <= '\u04FF':
            cyrillic_count += 1
        elif 'a' <= ch.lower() <= 'z':
            latin_count += 1
    if cyrillic_count > latin_count:
        return "kirill"
    return "lotin"


# ==================== RASM YAXSHILASH ====================

def _enhance_image(img: Image.Image) -> Image.Image:
    """Rasm sifatini avtomatik yaxshilash — OCR uchun optimallash."""
    try:
        # Kontrast oshirish
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.4)
        
        # Aniqlik (sharpness) oshirish
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.6)
        
        # Yorug'lik biroz oshirish
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(1.1)
    except Exception as e:
        logging.warning(f"Rasm yaxshilashda xato: {e}")
    
    return img


# ==================== RASM QAYTA ISHLASH ====================

async def process_image_async(image_path: str, alphabet: str) -> tuple:
    import json
    image = await asyncio.to_thread(_open_and_optimize_image, image_path)
    
    prompt = (
        f"Analyze this document image. We are reconstructing the layout automatically. "
        f"1. Extract all text completely and translate/convert it carefully into the {alphabet} alphabet. "
        f"2. Identify the `text_bottom_y` (0-1000 scale) coordinate where the LAST line of the text block above the diagram ends. "
        f"3. Identify the bounding boxes of ONLY the non-text pure graphical elements (e.g. the exact outline of the engine or device). "
        f"CRITICAL: The graphical diagram's bounding box `ymin` MUST be strictly greater than `text_bottom_y` to ensure no text is included in the bounding box. "
        f"Return ONLY valid JSON exactly like this: "
        f"{{\n"
        f"  \"text\": \"full extracted and converted text\",\n"
        f"  \"text_bottom_y\": 250,\n"
        f"  \"diagrams\": [ {{\"box_2d\": [ymin, xmin, ymax, xmax]}} ]\n"
        f"}}\n"
        f"If there are no physical diagrams, leave the diagrams array empty."
    )

    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        if response.text:
            try:
                # Tozalash: Gemini ko'pincha markdown kod bloklaridan foydalanadi (```json ... ```)
                raw_json = response.text
                if raw_json.startswith("```json"):
                    raw_json = raw_json[7:]
                if raw_json.startswith("```"):
                    raw_json = raw_json[3:]
                if raw_json.endswith("```"):
                    raw_json = raw_json[:-3]
                raw_json = raw_json.strip()
                
                data = json.loads(raw_json)
                text_result = data.get("text", "").strip()
                diagrams = data.get("diagrams", [])
                
                cropped_path = None
                if diagrams and len(diagrams) > 0:
                    box = None
                    diagram_item = diagrams[0]
                    if isinstance(diagram_item, dict):
                        box = diagram_item.get("box_2d", diagram_item.get("box_3d"))
                    elif isinstance(diagram_item, list):
                        box = diagram_item
                    
                    if isinstance(box, list) and len(box) == 4:
                        try:
                            ymin, xmin, ymax, xmax = [int(v) for v in box]
                            # Qat'iy mantiqiy chegara: Diagramma ymin matn ymax'sidan kattaroq bo'lishi shart!
                            text_bottom = int(data.get("text_bottom_y", 0))
                            if text_bottom > 0 and text_bottom < ymax:
                                ymin = max(ymin, text_bottom + 5) 
                            
                            # Agresiv tozalash: AIda xato ketsa ham yozuvlari kirmasligini ta'minlash
                            ymin = min(ymin + 65, ymax - 30)
                            ymax = max(ymax - 25, ymin + 20)
                            xmin = min(xmin + 25, xmax - 10)
                            xmax = max(xmax - 20, xmin + 10)
                            
                            w, h = image.size
                            left = int(xmin * w / 1000)
                            top = int(ymin * h / 1000)
                            right = int(xmax * w / 1000)
                            bottom = int(ymax * h / 1000)
                            
                            # Faqat yaroqli koordinatalar bo'lsa
                            if right > left and bottom > top:
                                cropped = image.crop((left, top, right, bottom))
                                cropped_path = f"{image_path}_crop.jpg"
                                if cropped.mode in ("RGBA", "P"):
                                    cropped = cropped.convert("RGB")
                                cropped.save(cropped_path, "JPEG", quality=95)
                        except Exception as parse_err:
                            logging.error(f"Kordinata xatoligi: {parse_err}")
                
                return text_result, cropped_path
                
            except Exception as e:
                logging.error(f"JSON parsing error yoki rasm kesishda xato: {e}")
                # Hato ketib qolsa, return response.text qilmasdan json textni tozalab olamiz
                import re
                fallback_text = response.text
                if '"text":' in fallback_text:
                    try:
                        clean_text = re.search(r'"text":\s*"([^"]+)"', fallback_text).group(1)
                        return clean_text, None
                    except:
                        pass
                return fallback_text.replace("{", "").replace("}", "").replace("[", "").replace("]", ""), None
        else:
            raise ValueError("Gemini API bo'sh javob qaytardi.")
    except Exception as e:
        logging.error(f"Gemini API xatolik: {e}")
        raise


def _open_and_optimize_image(image_path: str) -> Image.Image:
    img = Image.open(image_path)
    max_dimension = 2048
    if img.width > max_dimension or img.height > max_dimension:
        img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
    if img.mode == 'RGBA':
        bg = Image.new('RGB', img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Avtomatik rasm yaxshilash
    img = _enhance_image(img)
    
    return img


# ==================== MATN TARJIMASI ====================

async def translate_text(text: str, target_lang: str) -> str:
    """Matnni boshqa tilga tarjima qilish."""
    lang_map = {
        "uz_ru": "O'zbek tilidan Rus tiliga",
        "ru_uz": "Rus tilidan O'zbek tiliga", 
        "uz_en": "O'zbek tilidan Ingliz tiliga",
        "en_uz": "Ingliz tilidan O'zbek tiliga",
    }
    direction = lang_map.get(target_lang, "boshqa tilga")
    
    prompt = (
        f"{direction} tarjima qiling. Mazmunini o'zgartirmang.\n"
        f"Faqat tarjima qilingan matnni qaytaring, boshqa hech narsa qo'shmang.\n\n"
        f"Matn:\n{text}"
    )
    
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt]
        )
        if response.text:
            return response.text.strip()
        return text
    except Exception as e:
        logging.error(f"Tarjima xatolik: {e}")
        return text


# ==================== OVOZLI XABAR ====================

async def process_voice_async(voice_path: str, alphabet: str) -> str:
    """Ovozli xabarni matnga aylantirish. SpeechRecognition + Gemini fallback."""
    
    # 1-usul: SpeechRecognition (Google Speech API - bepul, ishonchli)
    try:
        logging.info("Ovoz: SpeechRecognition usuli sinab ko'rilmoqda...")
        text = await asyncio.to_thread(_speech_recognition_sync, voice_path)
        if text and len(text.strip()) > 2:
            logging.info(f"Ovoz: SpeechRecognition muvaffaqiyatli! ({len(text)} belgi)")
            # Agar alifbo konversiyasi kerak bo'lsa
            if alphabet == "Kirill":
                from utils import convert_latin_to_cyrillic
                text = convert_latin_to_cyrillic(text)
            return text.strip()
    except Exception as e:
        logging.warning(f"Ovoz: SpeechRecognition ishlamadi: {e}")
    
    # 2-usul: Gemini API (proxy orqali, 20 soniya timeout)
    try:
        logging.info("Ovoz: Gemini API sinab ko'rilmoqda (20s)...")
        with open(voice_path, 'rb') as f:
            audio_data = f.read()
        
        prompt = (
            f"Ushbu ovozli xabardagi gapni to'liq va aniq yozing. "
            f"Hech narsa qo'shmang, hech narsa tushirmang. "
            f"Imlo xatolarini tuzating. "
            f"Natijani {alphabet} alifbosida qaytaring. "
            f"Faqat matnni qaytaring."
        )
        
        contents = [
            {
                "inline_data": {
                    "mime_type": "audio/ogg",
                    "data": base64.b64encode(audio_data).decode()
                }
            },
            prompt
        ]
        
        response = await asyncio.wait_for(
            client.aio.models.generate_content(
                model='gemini-2.0-flash',
                contents=contents
            ),
            timeout=20.0
        )
        if response.text:
            result = response.text.strip().replace("**", "")
            logging.info("Ovoz: Gemini API muvaffaqiyatli!")
            return result
    except asyncio.TimeoutError:
        logging.warning("Ovoz: Gemini API 20 soniyada javob bermadi.")
    except Exception as e:
        logging.warning(f"Ovoz: Gemini API xato: {e}")
    
    raise Exception("Ovoz tahlili barcha usullarda muvaffaqiyatsiz. Iltimos, qayta urinib ko'ring.")


def _speech_recognition_sync(voice_path: str) -> str:
    """SpeechRecognition bilan sinxron ovoz tahlili."""
    import subprocess
    import sys
    import tempfile
    
    # speech_recognition va pydub o'rnatish (agar yo'q bo'lsa)
    try:
        import speech_recognition as sr
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "SpeechRecognition", "pydub"], 
                      capture_output=True, timeout=60)
        import speech_recognition as sr
    
    # OGG -> WAV konvertatsiya (ffmpeg yoki pydub orqali)
    wav_path = voice_path + ".wav"
    
    try:
        # ffmpeg orqali konvertatsiya (eng ishonchli)
        result = subprocess.run(
            ["ffmpeg", "-i", voice_path, "-ar", "16000", "-ac", "1", "-y", wav_path],
            capture_output=True, timeout=30
        )
        if result.returncode != 0:
            raise Exception("ffmpeg ishlamadi")
    except (FileNotFoundError, Exception):
        # pydub orqali
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_ogg(voice_path)
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(wav_path, format="wav")
        except Exception as e:
            raise Exception(f"Ovoz faylini WAV ga o'tkazib bo'lmadi: {e}")
    
    # Speech Recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = recognizer.record(source)
    
    # Tozalash
    try:
        os.remove(wav_path)
    except:
        pass
    
    # Google Speech Recognition (bepul, 50 ta so'rovgacha)
    try:
        text = recognizer.recognize_google(audio, language="uz-UZ")
        return text
    except sr.UnknownValueError:
        # O'zbek tilida topolmasa ruscha sinab ko'rish
        try:
            text = recognizer.recognize_google(audio, language="ru-RU")
            return text
        except:
            pass
    except Exception:
        pass
    
    # Oxirgi iloj - inglizcha
    try:
        text = recognizer.recognize_google(audio, language="en-US")
        return text
    except Exception as e:
        raise Exception(f"Google Speech API ham ishlamadi: {e}")


# ==================== SIFAT BALLI ====================

async def calculate_quality_score(text: str) -> dict:
    """Hujjat sifatini AI bilan baholash."""
    prompt = (
        "Quyidagi matnning sifatini 3 ta mezon bo'yicha 0-100 ball bilan baholang:\n"
        "1. OCR aniqligi (imlo, to'liqlik)\n"
        "2. Formatlash sifati (paragraflar, tuzilish)\n"
        "3. Grammatika va tinish belgilari\n\n"
        "Faqat 3 ta sonni qaytaring, vergul bilan ajratilgan. Masalan: 95,88,92\n"
        "Boshqa hech narsa yozmang.\n\n"
        f"Matn:\n{text[:2000]}"
    )
    
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt]
        )
        if response.text:
            scores = response.text.strip().replace(" ", "").split(",")
            if len(scores) >= 3:
                ocr = min(100, max(0, int(scores[0])))
                formatting = min(100, max(0, int(scores[1])))
                grammar = min(100, max(0, int(scores[2])))
                overall = round((ocr + formatting + grammar) / 3)
                return {
                    "ocr": ocr,
                    "formatting": formatting,
                    "grammar": grammar,
                    "overall": overall,
                }
    except Exception as e:
        logging.warning(f"Sifat balli xatolik: {e}")
    
    return {"ocr": 0, "formatting": 0, "grammar": 0, "overall": 0}

