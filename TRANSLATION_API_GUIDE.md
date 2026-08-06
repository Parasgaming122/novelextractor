# 📚 Novel Translation API Guide

This guide documents the complete translation engine architecture for the FastAPI novel reading platform.

## 🏗️ Architecture Overview

```
webapp/
├── services/
│   ├── __init__.py
│   ├── custom_scrapers.py      # FreeBingTranslator (no API key)
│   └── translation_core.py     # CompleteNovelTranslationManager
├── routers/
│   ├── __init__.py
│   └── translate_router.py     # FastAPI endpoints
└── main.py                     # Main application with router included
```

## 🔧 Available Translation Engines

### Free Engines (No API Key Required)

| Engine ID | Name | Description |
|-----------|------|-------------|
| `google_free` | Google Translate | Web scraping via deep-translator |
| `bing_free` | Bing Translator | Custom scraper, no key needed |
| `mymemory_free` | MyMemory | Community translations |
| `pons_free` | PONS Dictionary | Best for terms/slang |
| `linguee_free` | Linguee | Contextual translations |
| `libre_free` | LibreTranslate | Open source engine |

### Premium Engines (API Key Required)

| Engine ID | Name | Key Field | Description |
|-----------|------|-----------|-------------|
| `gemini_premium` | Google Gemini AI | `gemini_key` | Literary quality translations |
| `openai_premium` | OpenAI GPT-4o | `openai_key` | Natural fluent English |
| `deepl_premium` | DeepL Pro | `deepl_key` | Professional grade |
| `microsoft_premium` | Microsoft Translator | `microsoft_key` | Azure Cognitive Services |
| `baidu_premium` | Baidu Translate | `baidu_appid`, `baidu_secret` | Chinese specialist |
| `yandex_premium` | Yandex Translate | `yandex_key` | Russian search engine |

## 📡 API Endpoints

### 1. List Available Engines

```http
GET /api/v1/novel/engines
```

**Response:**
```json
{
  "google_free": {
    "name": "Google Translate (Free)",
    "type": "free",
    "requires_key": false,
    "available": true
  },
  "gemini_premium": {
    "name": "Google Gemini AI",
    "type": "premium",
    "requires_key": true,
    "key_name": "gemini_key",
    "available": true
  }
}
```

### 2. Translate Chapter

```http
POST /api/v1/novel/translate-chapter
Content-Type: application/json
```

**Request Body (Free Engine):**
```json
{
  "chapter_content": "这是一个测试章节。主角重生了!",
  "engine_selection": "google_free"
}
```

**Request Body (Premium Engine):**
```json
{
  "chapter_content": "这是一个测试章节。主角重生了!",
  "engine_selection": "gemini_premium",
  "user_keys": {
    "gemini_key": "AIzaSy..."
  }
}
```

**Response:**
```json
{
  "status": "success",
  "engine": "google_free",
  "translated_result": "This is a test chapter. The protagonist is reborn!",
  "character_count": 15,
  "chunk_count": 1
}
```

### 3. Batch Translate Paragraphs

```http
POST /api/v1/novel/translate-batch
Content-Type: application/json
```

**Request Body:**
```json
{
  "paragraphs": ["第一章：开始", "他睁开眼睛。", "这是一个新世界。"],
  "engine": "google_free"
}
```

**Response:**
```json
{
  "status": "success",
  "engine": "google_free",
  "results": [
    "Chapter 1: Beginning",
    "He opened his eyes.",
    "This is a new world."
  ],
  "count": 3
}
```

## ⚠️ Vercel Serverless Considerations

### Timeout Limits

| Plan | Max Duration | Recommendation |
|------|--------------|----------------|
| Hobby (Free) | 10 seconds | Use batch endpoint with small chunks |
| Pro | 60 seconds | Can handle full chapters |

### Configuration (vercel.json)

```json
{
  "version": 2,
  "builds": [
    {
      "src": "webapp/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "webapp/main.py"
    }
  ],
  "functions": {
    "webapp/main.py": {
      "maxDuration": 60
    }
  },
  "env": {
    "PYTHONPATH": "."
  }
}
```

### Best Practices for Vercel

1. **Frontend Chunking**: Split large chapters in your frontend JavaScript before sending to API
2. **Use Batch Endpoint**: Send 3-5 paragraphs at a time for hobby tier
3. **Proxy Rotation**: For free engines, populate `PROXY_POOL` in `translation_core.py`
4. **Premium APIs**: Work without proxies on Vercel (no IP blocking)

## 💻 Usage Examples

### Python Client

```python
import requests

# Get available engines
response = requests.get('https://your-vercel-app.vercel.app/api/v1/novel/engines')
engines = response.json()

# Translate with free engine
payload = {
    'chapter_content': '这是一个简单的测试。',
    'engine_selection': 'google_free'
}
response = requests.post(
    'https://your-vercel-app.vercel.app/api/v1/novel/translate-chapter',
    json=payload
)
result = response.json()
print(result['translated_result'])

# Translate with premium engine
payload = {
    'chapter_content': '这是一个简单的测试。',
    'engine_selection': 'openai_premium',
    'user_keys': {
        'openai_key': 'sk-proj-...'
    }
}
response = requests.post(
    'https://your-vercel-app.vercel.app/api/v1/novel/translate-chapter',
    json=payload
)
```

### JavaScript/Frontend

```javascript
// Get available engines
const engines = await fetch('/api/v1/novel/engines').then(r => r.json());

// Translate chapter
const response = await fetch('/api/v1/novel/translate-chapter', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    chapter_content: '这是一个测试章节。',
    engine_selection: 'bing_free'
  })
});

const result = await response.json();
console.log(result.translated_result);

// Batch translate (recommended for Vercel hobby tier)
const paragraphs = ['第一段', '第二段', '第三段'];
const response = await fetch('/api/v1/novel/translate-batch', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    paragraphs: paragraphs,
    engine: 'google_free'
  })
});

const { results } = await response.json();
```

## 🔑 Installing Dependencies

```bash
# Install all dependencies
pip install -r webapp/requirements.txt

# Or install individually
pip install fastapi uvicorn jinja2 python-multipart
pip install requests beautifulsoup4 lxml
pip install deep-translator>=1.11.4
pip install google-generativeai>=0.3.0
pip install openai>=1.0.0
```

## 🧪 Testing

```python
from fastapi.testclient import TestClient
from webapp.main import app

client = TestClient(app)

# Test engines endpoint
response = client.get('/api/v1/novel/engines')
print(response.json())

# Test translation
response = client.post('/api/v1/novel/translate-chapter', json={
    'chapter_content': '这是一个测试。',
    'engine_selection': 'google_free'
})
print(response.json())
```

## 🛠️ Adding Custom Proxies

For improved reliability with free engines on Vercel:

```python
# In webapp/services/translation_core.py
PROXY_POOL = [
    "http://proxy1.example.com:8080",
    "http://proxy2.example.com:8080",
    "http://proxy3.example.com:8080"
]
```

The translation manager will automatically rotate through proxies when encountering 429 rate limit errors.

---

**Note**: This architecture supports 11 translation engines total (5 free + 6 premium), with automatic fallback handling and chunking for large texts.
