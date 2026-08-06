"""
FastAPI Router for Novel Translation Endpoints
Handles request validation and dispatches to translation engines
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, List

from webapp.services.translation_core import CompleteNovelTranslationManager

router = APIRouter(prefix="/api/v1/novel", tags=["Novel Translation Engine"])


class PremiumKeysPayload(BaseModel):
    """
    Flexible container mapping to user settings for premium translation APIs.
    Only required when using premium engine selections.
    """
    gemini_key: Optional[str] = Field(None, description="Google Gemini API key", example="AIzaSy...")
    openai_key: Optional[str] = Field(None, description="OpenAI API key", example="sk-proj-...")
    deepl_key: Optional[str] = Field(None, description="DeepL API key", example="1234-5678...")
    deepl_tier: Optional[str] = Field("free", description="DeepL tier: 'free' or 'pro'")
    microsoft_key: Optional[str] = Field(None, description="Microsoft Translator API key", example="ms-azure-key...")
    baidu_appid: Optional[str] = Field(None, description="Baidu Translate App ID", example="2021000...")
    baidu_secret: Optional[str] = Field(None, description="Baidu Translate Secret Key", example="secret_app_pass...")
    yandex_key: Optional[str] = Field(None, description="Yandex Translate API key", example="yandex-passthrough...")


class CustomPromptPayload(BaseModel):
    """
    Custom translation prompts for AI-powered engines.
    Only used with gemini_premium and openai_premium engines.
    """
    gemini_prompt: Optional[str] = Field(
        None, 
        description="Custom prompt for Gemini AI translation",
        example="Translate this Chinese novel text to narrative English, maintaining the original tone and style:"
    )
    openai_prompt: Optional[str] = Field(
        None,
        description="Custom system prompt for OpenAI translation",
        example="You are a professional literary translator specializing in Chinese web novels. Translate this text to fluent, natural English while preserving cultural nuances:"
    )


class NovelTranslationSchema(BaseModel):
    """
    Request schema for novel chapter translation
    """
    chapter_content: str = Field(
        ..., 
        description="Raw Chinese content payload",
        min_length=1,
        max_length=50000  # Prevent excessively large payloads
    )
    engine_selection: str = Field(
        "google_free", 
        description="Translation engine selection",
        example="google_free"
    )
    user_keys: Optional[PremiumKeysPayload] = Field(
        None, 
        description="API keys for premium engines (optional for free engines)"
    )
    custom_prompt: Optional[str] = Field(
        None,
        description="Custom translation prompt for AI engines (overrides default prompts)",
        example="Translate this wuxia novel text maintaining martial arts terminology:"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "chapter_content": "这是一个测试文本。",
                "engine_selection": "bing_free",
                "user_keys": None,
                "custom_prompt": None
            }
        }


class TranslationResponse(BaseModel):
    """
    Response schema for translation results
    """
    status: str
    engine: str
    translated_result: str
    character_count: int
    chunk_count: Optional[int] = None


@router.post("/translate-chapter", response_model=TranslationResponse)
async def process_translation(payload: NovelTranslationSchema):
    """
    Translate a novel chapter using the selected engine.
    
    - **chapter_content**: Raw Chinese text to translate (max 50,000 characters)
    - **engine_selection**: Choose from free or premium engines
    - **user_keys**: API keys required only for premium engines
    
    ## Free Engines (No API Key Required):
    - `google_free` - Google Translate via web scraping
    - `bing_free` - Bing Translator via web scraping  
    - `mymemory_free` - MyMemory community translations
    - `pons_free` - PONS dictionary (best for terms/slang)
    - `linguee_free` - Linguee contextual translations
    - `libre_free` - LibreTranslate open source
    
    ## Premium Engines (API Key Required):
    - `gemini_premium` - Google Gemini AI (literary quality)
    - `openai_premium` - OpenAI GPT-4o (natural fluency)
    - `deepl_premium` - DeepL Pro (professional grade)
    - `microsoft_premium` - Microsoft Translator API
    - `baidu_premium` - Baidu Translate (Chinese specialist)
    - `yandex_premium` - Yandex Translate
    
    ⚠️ **Vercel Serverless Note**: For hobby tier (10s timeout), 
    consider chunking large chapters in your frontend before sending.
    """
    # Validate content is not empty after stripping whitespace
    if not payload.chapter_content.strip():
        raise HTTPException(
            status_code=400, 
            detail="Text body data can not be empty."
        )
    
    # Validate engine selection
    available_engines = CompleteNovelTranslationManager.get_available_engines()
    if payload.engine_selection not in available_engines:
        valid_engines = list(available_engines.keys())
        raise HTTPException(
            status_code=400,
            detail=f"Invalid engine selection. Valid options: {', '.join(valid_engines)}"
        )
    
    # Check if premium engine requires API key
    engine_info = available_engines[payload.engine_selection]
    if engine_info.get("requires_key") and not payload.user_keys:
        raise HTTPException(
            status_code=400,
            detail=f"Engine '{payload.engine_selection}' requires API credentials. Please provide user_keys."
        )
    
    # Safe structure conversion initialization
    api_keys: Dict[str, str] = {}
    if payload.user_keys:
        api_keys = payload.user_keys.model_dump(exclude_unset=True)
    
    try:
        # Calculate chunk count for response metadata
        char_count = len(payload.chapter_content)
        chunk_size = CompleteNovelTranslationManager.MAX_CHUNK_SIZE
        estimated_chunks = max(1, char_count // chunk_size + (1 if char_count % chunk_size else 0))
        
        translated_text = CompleteNovelTranslationManager.translate_novel(
            full_text=payload.chapter_content,
            engine=payload.engine_selection,
            keys=api_keys,
            custom_prompt=payload.custom_prompt
        )
        
        return TranslationResponse(
            status="success",
            engine=payload.engine_selection,
            translated_result=translated_text,
            character_count=char_count,
            chunk_count=estimated_chunks
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )


@router.get("/engines", response_model=Dict[str, Dict])
async def list_engines():
    """
    List all available translation engines with their requirements.
    Useful for populating frontend dropdown menus.
    """
    return CompleteNovelTranslationManager.get_available_engines()


@router.post("/translate-batch")
async def process_batch_translation(
    paragraphs: List[str],
    engine: str = "google_free",
    user_keys: Optional[PremiumKeysPayload] = None,
    custom_prompt: Optional[str] = None
):
    """
    Translate multiple paragraphs independently (parallelizable).
    Useful for frontend-driven chunking to avoid Vercel timeout limits.
    
    Returns translations in the same order as input paragraphs.
    
    Request body:
    - **paragraphs**: List of paragraph strings to translate
    - **engine**: Translation engine (default: google_free)
    - **user_keys**: Optional API keys for premium engines
    - **custom_prompt**: Optional custom translation prompt for AI engines
    """
    if not paragraphs:
        raise HTTPException(status_code=400, detail="Paragraphs list cannot be empty")
    
    api_keys: Dict[str, str] = {}
    if user_keys:
        api_keys = user_keys.model_dump(exclude_unset=True)
    
    results = []
    for para in paragraphs:
        if para.strip():
            translated = CompleteNovelTranslationManager.translate_chunk(
                text=para.strip(),
                engine=engine,
                keys=api_keys,
                custom_prompt=custom_prompt
            )
            results.append(translated)
        else:
            results.append("")
    
    return {
        "status": "success",
        "engine": engine,
        "results": results,
        "count": len(results)
    }
