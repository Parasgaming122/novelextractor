"""
FastAPI Novel Reading Web Application
Vercel-compatible deployment
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add parent directory to path to import scraper modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from universal_novel_scraper import search_novel, fetch_novel_info, extract_chapter_content
from bypasser import fetch as bypasser_fetch

# Import translation router
from webapp.routers.translate_router import router as translate_router

app = FastAPI(title="Novel Reader", description="A modern novel reading platform with TTS support")

# Include translation router
app.include_router(translate_router)

# Enable CORS for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))


@app.get("/", response_class=HTMLResponse)
async def homepage(request: Request):
    """Render the homepage"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/sources", response_class=HTMLResponse)
async def sources_page(request: Request):
    """Render the sources page"""
    return templates.TemplateResponse("sources.html", {"request": request})


@app.get("/search", response_class=HTMLResponse)
async def search_page(request: Request):
    """Render the search page"""
    return templates.TemplateResponse("search.html", {"request": request})


@app.get("/favourites", response_class=HTMLResponse)
async def favourites_page(request: Request):
    """Render the favourites page"""
    return templates.TemplateResponse("favourites.html", {"request": request})


@app.get("/novel-info", response_class=HTMLResponse)
async def novel_info_page(request: Request):
    """Render the novel info page (not about page)"""
    return templates.TemplateResponse("novel-info.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
async def about_page(request: Request):
    """Render the about/info page"""
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/reader", response_class=HTMLResponse)
async def reader_page(request: Request):
    """Render the reader page"""
    return templates.TemplateResponse("reader.html", {"request": request})


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Render the settings page"""
    return templates.TemplateResponse("settings.html", {"request": request})


@app.get("/api/search")
async def api_search(q: str = Query(...), sep: bool = Query(False)):
    """
    Search for novels across multiple sources
    - q: search query
    - sep: if true, separate results by source
    """
    try:
        results = search_novel(q)
        
        if sep:
            # Group by source
            grouped = {}
            for r in results:
                source = r.source
                if source not in grouped:
                    grouped[source] = []
                grouped[source].append({
                    "title": r.title,
                    "url": r.url,
                    "author": getattr(r, 'author', ''),
                    "latest_chapter": getattr(r, 'latest_chapter', ''),
                    "cover_url": getattr(r, 'cover_url', None)
                })
            return {"grouped": True, "results": grouped}
        else:
            return {
                "grouped": False,
                "results": [
                    {
                        "title": r.title,
                        "url": r.url,
                        "author": getattr(r, 'author', ''),
                        "latest_chapter": getattr(r, 'latest_chapter', ''),
                        "cover_url": getattr(r, 'cover_url', None),
                        "source": r.source
                    }
                    for r in results
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/novel-info")
async def api_novel_info(url: str = Query(...)):
    """Get detailed novel information including chapter list"""
    try:
        info = fetch_novel_info(url)
        return {
            "title": info.title,
            "author": info.author,
            "status": info.status,
            "description": info.description,
            "cover_url": info.cover_url,
            "chapters": [
                {"title": ch.title, "url": ch.url}
                for ch in info.chapters
            ],
            "source": info.source
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chapter")
async def api_chapter(url: str = Query(...), translate: bool = Query(False), engine: str = Query("google_free")):
    """Extract chapter content with optional translation
    
    Query Parameters:
        - url: Chapter URL to extract content from
        - translate: Whether to translate the content (default: false)
        - engine: Translation engine to use (default: google_free)
            Options: google_free, bing_free, mymemory_free, pons_free, linguee_free, libre_free
    """
    try:
        content = extract_chapter_content(url)
        result = {
            "title": content['title'],
            "content": content['content'],
            "confidence": content['confidence'],
            "url": url
        }
        
        # If translation is requested, use the translation service
        if translate:
            from webapp.services.translation_core import CompleteNovelTranslationManager
            
            # Validate engine selection
            available_engines = CompleteNovelTranslationManager.get_available_engines()
            if engine not in available_engines or not available_engines[engine].get('available', False):
                engine = "google_free"  # Fallback to default
            
            try:
                translated = CompleteNovelTranslationManager.translate_novel(
                    full_text=result["content"],
                    engine=engine,
                    keys={},
                    custom_prompt=None
                )
                result["translated_content"] = translated
                result["is_translated"] = True
                result["translation_engine"] = engine
            except Exception as trans_error:
                # If translation fails, log but don't fail the request
                result["translation_error"] = str(trans_error)
                result["is_translated"] = False
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/feed")
async def api_feed(source: str = Query(None), page: int = Query(1)):
    """Get home feed from sources"""
    try:
        from universal_novel_scraper import get_home_feed
        if source:
            feed = get_home_feed(source, page=page)
        else:
            feed = get_home_feed(page=page)
        
        return {
            "results": [
                {
                    "title": item.title,
                    "url": item.url,
                    "cover_url": item.cover_url,
                    "latest_chapter": item.latest_chapter,
                    "source": item.source
                }
                for item in feed
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
