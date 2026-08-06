# API Reference

Complete REST API documentation for the Novel Reader platform.

## Base URL

When running locally: `http://localhost:8000`

When deployed to Vercel: `https://your-project.vercel.app`

---

## Search & Discovery APIs

### Search Novels

Search for novels across all supported sources.

**Endpoint:** `GET /api/search`

**Parameters:**

| Parameter | Type   | Required | Description                                      |
|-----------|--------|----------|--------------------------------------------------|
| `q`       | string | Yes      | Search query (novel title, author, keywords)     |
| `sep`     | bool   | No       | If true, groups results by source (default: false) |

**Example Request:**
```bash
curl "http://localhost:8000/api/search?q=%E6%B4%AA%E8%8D%92&sep=false"
```

**Example Response:**
```json
{
  "grouped": false,
  "results": [
    {
      "title": "洪荒：我開局打造鴻蒙金榜",
      "url": "https://ixdzs8.com/book/123",
      "author": "作者名",
      "latest_chapter": "Chapter 500",
      "cover_url": "https://...",
      "source": "ixdzs8"
    }
  ]
}
```

---

### Get Home Feed

Get hot novels and recommendations from sources.

**Endpoint:** `GET /api/feed`

**Parameters:**

| Parameter | Type   | Required | Description                                                                 |
|-----------|--------|----------|-----------------------------------------------------------------------------|
| `source`  | string | No       | Specific source (ixdzs8, shuhaige, biquge, ttkan, xbiquge). Omit for all   |
| `page`    | int    | No       | Page number for pagination (default: 1)                                     |

**Example Request:**
```bash
curl "http://localhost:8000/api/feed?source=ixdzs8&page=1"
```

**Example Response:**
```json
{
  "results": [
    {
      "title": "Popular Novel",
      "url": "https://...",
      "cover_url": "https://...",
      "latest_chapter": "Chapter 100",
      "source": "ixdzs8"
    }
  ]
}
```

---

## Novel Information APIs

### Get Novel Details

Retrieve complete novel metadata including chapter list.

**Endpoint:** `GET /api/novel-info`

**Parameters:**

| Parameter | Type   | Required | Description              |
|-----------|--------|----------|--------------------------|
| `url`     | string | Yes      | Novel detail page URL    |

**Example Request:**
```bash
curl "http://localhost:8000/api/novel-info?url=https%3A%2F%2Fixdzs8.com%2Fbook%2F123"
```

**Example Response:**
```json
{
  "title": "洪荒：我開局打造鴻蒙金榜",
  "author": "作者名",
  "status": "Ongoing",
  "description": "故事简介...",
  "cover_url": "https://...",
  "chapters": [
    {"title": "Chapter 1", "url": "https://..."},
    {"title": "Chapter 2", "url": "https://..."}
  ],
  "source": "ixdzs8"
}
```

---

### Extract Chapter Content

Extract clean chapter text from a chapter URL.

**Endpoint:** `GET /api/chapter`

**Parameters:**

| Parameter | Type   | Required | Description          |
|-----------|--------|----------|----------------------|
| `url`     | string | Yes      | Chapter URL to extract |

**Example Request:**
```bash
curl "http://localhost:8000/api/chapter?url=https%3A%2F%2Fixdzs8.com%2Fread%2F123%2Fp1"
```

**Example Response:**
```json
{
  "title": "Chapter 1: Rebirth",
  "content": "The primordial world!\n\nA mysterious island...",
  "confidence": 0.95,
  "url": "https://..."
}
```

---

## Translation Engine APIs

### List Available Engines

Get all translation engines with their requirements.

**Endpoint:** `GET /api/v1/novel/engines`

**Example Response:**
```json
{
  "google_free": {
    "name": "Google Translate (Free)",
    "requires_key": false,
    "description": "Web scraping based Google Translate"
  },
  "gemini_premium": {
    "name": "Google Gemini AI",
    "requires_key": true,
    "description": "Literary quality translation with AI"
  }
}
```

---

### Translate Chapter

Translate novel chapter using selected engine.

**Endpoint:** `POST /api/v1/novel/translate-chapter`

**Request Body:**
```json
{
  "chapter_content": "这是要翻译的中文文本。",
  "engine_selection": "google_free",
  "user_keys": {
    "gemini_key": "AIzaSy...",
    "openai_key": "sk-proj-...",
    "deepl_key": "1234-5678...",
    "deepl_tier": "free",
    "microsoft_key": "ms-azure-key...",
    "baidu_appid": "2021000...",
    "baidu_secret": "secret...",
    "yandex_key": "yandex-key..."
  },
  "custom_prompt": "Translate this wuxia novel maintaining martial arts terminology"
}
```

**Available Engines:**

**Free (No API Key):**
- `google_free` - Google Translate
- `bing_free` - Bing Translator
- `mymemory_free` - MyMemory
- `pons_free` - PONS Dictionary
- `linguee_free` - Linguee
- `libre_free` - LibreTranslate

**Premium (API Key Required):**
- `gemini_premium` - Google Gemini AI
- `openai_premium` - OpenAI GPT-4o
- `deepl_premium` - DeepL Pro
- `microsoft_premium` - Microsoft Translator
- `baidu_premium` - Baidu Translate
- `yandex_premium` - Yandex Translate

**Example Response:**
```json
{
  "status": "success",
  "engine": "google_free",
  "translated_result": "This is the translated text.",
  "character_count": 150,
  "chunk_count": 1
}
```

---

### Batch Translate Paragraphs

Translate multiple paragraphs independently (Vercel-friendly).

**Endpoint:** `POST /api/v1/novel/translate-batch`

**Request Body:**
```json
{
  "paragraphs": ["第一段", "第二段", "第三段"],
  "engine": "google_free",
  "user_keys": {...},
  "custom_prompt": "Custom translation prompt"
}
```

**Example Response:**
```json
{
  "status": "success",
  "engine": "google_free",
  "results": ["First paragraph", "Second paragraph", "Third paragraph"],
  "count": 3
}
```

> **Vercel Serverless Note:** For hobby tier (10s timeout), use batch translation in your frontend to send smaller chunks (3-5 paragraphs per request).

---

## Error Handling

The API uses standard HTTP status codes:

| Status Code | Meaning         | Description                                    |
|-------------|-----------------|------------------------------------------------|
| `200`       | OK              | Request successful                             |
| `400`       | Bad Request     | Invalid parameters or missing required fields  |
| `404`       | Not Found       | Endpoint or resource not found                 |
| `500`       | Server Error    | Internal server error during processing        |
| `504`       | Gateway Timeout | Request timeout (common on Vercel free tier)   |

**Error Response Format:**
```json
{
  "detail": "Error message description"
}
```

---

## Supported Sources

| Source           | Base URL                        | Search | Feed            | Covers |
|------------------|---------------------------------|--------|-----------------|--------|
| **ixdzs8**       | https://ixdzs8.com             | ✅     | ✅ `/hot/day/`  | ✅     |
| **shuhaige**     | https://shuhaige.net           | ✅     | ✅ `/shuku/`    | ✅     |
| **biquge.company**| https://www.biquge.company    | ✅     | ✅ `/sort/0/`   | ✅     |
| **ttkan**        | https://www.ttkan.co           | ✅     | ✅ `/novel/rank`| ✅     |
| **xbiquge**      | https://www.xbiquge.info       | ✅     | ✅ `/top/`      | ✅     |

---

## Rate Limits & Best Practices

### Rate Limits

- **Self-hosted:** No limits (respect source websites' terms)
- **Vercel Free Tier:** 10-second timeout per request
- **Vercel Pro Tier:** Up to 5 minutes per request

### Best Practices

1. Use batch translation endpoint for large chapters on Vercel
2. Implement client-side caching to reduce API calls
3. Add delays between requests when scraping
4. Use cover images from cache when available
5. Respect robots.txt of source websites
