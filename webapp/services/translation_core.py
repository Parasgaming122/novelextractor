"""
Translation Core Module
Orchestrates multiple translation engines (free scrapers + premium APIs)
Supports 5 free web-scraping backends and 6 premium API options
"""
from typing import Optional, Dict, List
import os

# Import free scrapers
from webapp.services.custom_scrapers import FreeBingTranslator

# Try to import deep_translator (optional - for free engines)
try:
    from deep_translator import (
        GoogleTranslator,
        MyMemoryTranslator,
        PonsTranslator,
        LingueeTranslator,
        LibreTranslator
    )
    DEEP_TRANSLATOR_AVAILABLE = True
except ImportError:
    DEEP_TRANSLATOR_AVAILABLE = False

# Try to import premium AI libraries (optional)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from deep_translator import DeeplTranslator, MicrosoftTranslator, BaiduTranslator, YandexTranslator
    PREMIUM_TRANSLATORS_AVAILABLE = True
except ImportError:
    PREMIUM_TRANSLATORS_AVAILABLE = False


# Proxy pool for rate-limit bypass (populate with working proxies)
PROXY_POOL: List[str] = []


class CompleteNovelTranslationManager:
    """
    Manages translation of novel chapters across multiple engines.
    Supports chunking for large texts to fit within payload limits.
    """
    
    # Maximum characters per chunk to avoid payload limits
    MAX_CHUNK_SIZE = 1800
    
    # Default translation prompts for premium AI engines
    DEFAULT_PROMPTS = {
        "gemini_premium": "Translate this Chinese novel text to narrative English, maintaining the original tone and style:",
        "openai_premium": "You are a professional literary translator specializing in Chinese web novels. Translate this text to fluent, natural English while preserving cultural nuances:",
        "deepl_premium": "",  # DeepL doesn't use custom prompts
        "microsoft_premium": "",  # Microsoft doesn't use custom prompts
        "baidu_premium": "",  # Baidu doesn't use custom prompts
        "yandex_premium": ""  # Yandex doesn't use custom prompts
    }
    
    @staticmethod
    def translate_chunk(text: str, engine: str, keys: Dict[str, str], p_idx: int = 0, custom_prompt: Optional[str] = None) -> str:
        """
        Processes an isolated sequence block up to MAX_CHUNK_SIZE characters.
        
        Args:
            text: Text chunk to translate
            engine: Engine selection identifier
            keys: Dictionary of API keys for premium services
            p_idx: Proxy pool index for rotation
            
        Returns:
            Translated text or error message
        """
        proxy = None
        if PROXY_POOL and len(PROXY_POOL) > 0:
            proxy = {"http": PROXY_POOL[p_idx % len(PROXY_POOL)], 
                     "https": PROXY_POOL[p_idx % len(PROXY_POOL)]}
        
        try:
            # ==========================================
            # SECTION A: 100% FREE SCRAPING ENGINES (No API Key Required)
            # ==========================================
            
            if engine == "google_free":
                if not DEEP_TRANSLATOR_AVAILABLE:
                    return "[Error: deep_translator not installed]"
                return GoogleTranslator(source='zh-CN', target='en', proxies=proxy).translate(text)
            
            elif engine == "bing_free":
                return FreeBingTranslator().translate(text, from_lang="zh-Hans", to_lang="en")
                
            elif engine == "mymemory_free":
                if not DEEP_TRANSLATOR_AVAILABLE:
                    return "[Error: deep_translator not installed]"
                return MyMemoryTranslator(source='zh-CN', target='en', proxies=proxy).translate(text)
                
            elif engine == "pons_free":
                if not DEEP_TRANSLATOR_AVAILABLE:
                    return "[Error: deep_translator not installed]"
                # Primarily dictionary-based; optimal for processing isolated slang/terms
                return PonsTranslator(source='zh', target='en').translate(text)
                
            elif engine == "linguee_free":
                if not DEEP_TRANSLATOR_AVAILABLE:
                    return "[Error: deep_translator not installed]"
                return LingueeTranslator(source='zh', target='en').translate(text)

            elif engine == "libre_free":
                if not DEEP_TRANSLATOR_AVAILABLE:
                    return "[Error: deep_translator not installed]"
                # Connects to default open community mirror channels
                return LibreTranslator(source='zh', target='en').translate(text)

            # ==========================================
            # SECTION B: PREMIUM API ENGINES (Require API Keys)
            # ==========================================
            
            elif engine == "gemini_premium":
                if not GEMINI_AVAILABLE or not keys.get("gemini_key"):
                    return "[Error: Gemini API key required]"
                genai.configure(api_key=keys["gemini_key"])
                model = genai.GenerativeModel('gemini-1.5-flash')
                # Use custom prompt if provided, otherwise use default
                prompt = custom_prompt or CompleteNovelTranslationManager.DEFAULT_PROMPTS.get("gemini_premium", "")
                response = model.generate_content(
                    f"{prompt}\n\n{text}" if prompt else text
                )
                return response.text

            elif engine == "openai_premium":
                if not OPENAI_AVAILABLE or not keys.get("openai_key"):
                    return "[Error: OpenAI API key required]"
                client = OpenAI(api_key=keys["openai_key"])
                # Use custom prompt if provided, otherwise use default
                system_prompt = custom_prompt or CompleteNovelTranslationManager.DEFAULT_PROMPTS.get("openai_premium", "You are a professional literary translator specializing in Chinese web novels.")
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{
                        "role": "system", 
                        "content": system_prompt
                    }, {
                        "role": "user", 
                        "content": f"Translate this text to fluent, natural English:\n\n{text}"
                    }]
                )
                return response.choices[0].message.content

            elif engine == "deepl_premium":
                if not PREMIUM_TRANSLATORS_AVAILABLE or not keys.get("deepl_key"):
                    return "[Error: DeepL API key required]"
                # Dynamic switch handles user accounts targeting DeepL Pro vs Free plan API tokens
                is_free_tier = keys.get("deepl_tier", "free") == "free"
                return DeeplTranslator(
                    api_key=keys["deepl_key"], 
                    source="zh", 
                    target="en", 
                    use_free_api=is_free_tier
                ).translate(text)

            elif engine == "microsoft_premium":
                if not PREMIUM_TRANSLATORS_AVAILABLE or not keys.get("microsoft_key"):
                    return "[Error: Microsoft Translator API key required]"
                return MicrosoftTranslator(
                    api_key=keys["microsoft_key"], 
                    target="en"
                ).translate(text)

            elif engine == "baidu_premium":
                if not PREMIUM_TRANSLATORS_AVAILABLE or not keys.get("baidu_appid") or not keys.get("baidu_secret"):
                    return "[Error: Baidu API credentials required]"
                return BaiduTranslator(
                    appid=keys["baidu_appid"], 
                    appkey=keys["baidu_secret"], 
                    source="zh", 
                    target="en"
                ).translate(text)

            elif engine == "yandex_premium":
                if not PREMIUM_TRANSLATORS_AVAILABLE or not keys.get("yandex_key"):
                    return "[Error: Yandex API key required]"
                return YandexTranslator(api_key=keys["yandex_key"]).translate(
                    source="zh", 
                    target="en", 
                    text=text
                )

            # Default fallback to Google Free
            else:
                if DEEP_TRANSLATOR_AVAILABLE:
                    return GoogleTranslator(source='zh-CN', target='en').translate(text)
                return text

        except Exception as e:
            error_msg = str(e)
            
            # Network block proxy-shifting fail-safe
            if "429" in error_msg and PROXY_POOL and p_idx < len(PROXY_POOL):
                return CompleteNovelTranslationManager.translate_chunk(
                    text, engine, keys, p_idx + 1
                )
            
            # Cascade directly to standard free Google if engine initialization crashes
            if engine != "google_free" and DEEP_TRANSLATOR_AVAILABLE:
                try:
                    return CompleteNovelTranslationManager.translate_chunk(
                        text, "google_free", keys
                    )
                except:
                    pass
            
            return f"[Translation Error: {error_msg}]"

    @classmethod
    def translate_novel(cls, full_text: str, engine: str, keys: Dict[str, str], custom_prompt: Optional[str] = None) -> str:
        """
        Splits full web novel texts safely to fit under single text payloads.
        
        Args:
            full_text: Complete chapter text to translate
            engine: Engine selection identifier
            keys: Dictionary of API keys for premium services
            custom_prompt: Optional custom translation prompt for AI engines
            
        Returns:
            Fully translated chapter text
        """
        paragraphs = full_text.split('\n')
        translated_story = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) < cls.MAX_CHUNK_SIZE:
                current_chunk += para + "\n"
            else:
                if current_chunk.strip():
                    translated_story.append(
                        cls.translate_chunk(current_chunk.strip(), engine, keys, custom_prompt=custom_prompt)
                    )
                current_chunk = para + "\n"

        # Process remaining chunk
        if current_chunk.strip():
            translated_story.append(
                cls.translate_chunk(current_chunk.strip(), engine, keys, custom_prompt=custom_prompt)
            )

        return "\n".join(translated_story)

    @classmethod
    def get_available_engines(cls) -> Dict[str, Dict]:
        """
        Returns dictionary of available engines with their requirements.
        
        Returns:
            Dict mapping engine IDs to their metadata
        """
        engines = {
            # Free engines
            "google_free": {
                "name": "Google Translate (Free)",
                "type": "free",
                "requires_key": False,
                "available": DEEP_TRANSLATOR_AVAILABLE
            },
            "bing_free": {
                "name": "Bing Translator (Free)",
                "type": "free",
                "requires_key": False,
                "available": True
            },
            "mymemory_free": {
                "name": "MyMemory (Free)",
                "type": "free",
                "requires_key": False,
                "available": DEEP_TRANSLATOR_AVAILABLE
            },
            "pons_free": {
                "name": "PONS Dictionary (Free)",
                "type": "free",
                "requires_key": False,
                "available": DEEP_TRANSLATOR_AVAILABLE
            },
            "linguee_free": {
                "name": "Linguee (Free)",
                "type": "free",
                "requires_key": False,
                "available": DEEP_TRANSLATOR_AVAILABLE
            },
            "libre_free": {
                "name": "LibreTranslate (Free)",
                "type": "free",
                "requires_key": False,
                "available": DEEP_TRANSLATOR_AVAILABLE
            },
            # Premium engines
            "gemini_premium": {
                "name": "Google Gemini AI",
                "type": "premium",
                "requires_key": True,
                "key_name": "gemini_key",
                "available": GEMINI_AVAILABLE
            },
            "openai_premium": {
                "name": "OpenAI GPT-4o",
                "type": "premium",
                "requires_key": True,
                "key_name": "openai_key",
                "available": OPENAI_AVAILABLE
            },
            "deepl_premium": {
                "name": "DeepL Pro",
                "type": "premium",
                "requires_key": True,
                "key_name": "deepl_key",
                "available": PREMIUM_TRANSLATORS_AVAILABLE
            },
            "microsoft_premium": {
                "name": "Microsoft Translator",
                "type": "premium",
                "requires_key": True,
                "key_name": "microsoft_key",
                "available": PREMIUM_TRANSLATORS_AVAILABLE
            },
            "baidu_premium": {
                "name": "Baidu Translate",
                "type": "premium",
                "requires_key": True,
                "key_name": "baidu_appid",
                "available": PREMIUM_TRANSLATORS_AVAILABLE
            },
            "yandex_premium": {
                "name": "Yandex Translate",
                "type": "premium",
                "requires_key": True,
                "key_name": "yandex_key",
                "available": PREMIUM_TRANSLATORS_AVAILABLE
            }
        }
        return engines
