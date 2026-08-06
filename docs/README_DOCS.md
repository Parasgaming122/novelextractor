# Documentation Index

Welcome to the Novel Reader documentation. This guide covers all aspects of the platform.

## Quick Links

- **[API Reference](api.md)** - Complete REST API documentation with examples
- **[Usage Guide](usage.md)** - How to use the CLI and web app
- **[Architecture](architecture.md)** - System design and components
- **[Development](development.md)** - Contributing and extending the project

## Overview

Novel Reader is a complete web novel reading platform featuring:

1. **Multi-Source Search** - Search across 5+ Chinese novel websites
2. **Smart Extraction** - Intelligent chapter content extraction
3. **Translation Engine** - 12 translation engines (6 free + 6 premium)
4. **Text-to-Speech** - Listen to novels with customizable voices
5. **Modern Web UI** - Beautiful, responsive interface
6. **Vercel Ready** - Deploy instantly to serverless infrastructure

## Getting Started

### For Users

1. Visit the web app at your deployed URL or `http://localhost:8000`
2. Use the **Search** page to find novels
3. Click on any novel to view details and chapters
4. Read chapters with optional TTS or translation

### For Developers

```bash
# Clone and install
git clone <repository-url>
pip install -r webapp/requirements.txt

# Run locally
cd webapp
python main.py
```

See [Usage Guide](usage.md) for detailed instructions.

## API Quick Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/search` | GET | Search for novels |
| `/api/feed` | GET | Get hot novels feed |
| `/api/novel-info` | GET | Get novel details |
| `/api/chapter` | GET | Extract chapter content |

### Translation Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/novel/engines` | GET | List translation engines |
| `/api/v1/novel/translate-chapter` | POST | Translate a chapter |
| `/api/v1/novel/translate-batch` | POST | Batch translate paragraphs |

Full documentation: [API Reference](api.md)

## Supported Sources

| Source | URL | Features |
|--------|-----|----------|
| ixdzs8 | https://ixdzs8.com | Search, Feed, Covers |
| shuhaige | https://shuhaige.net | Search, Feed, Covers |
| biquge.company | https://www.biquge.company | Search, Feed, Covers |
| ttkan | https://www.ttkan.co | Search, Feed, Covers |
| xbiquge | https://www.xbiquge.info | Search, Feed, Covers |

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel login
vercel --prod
```

Configuration is handled automatically via `vercel.json`.

### Self-Hosted

```bash
uvicorn webapp.main:app --host 0.0.0.0 --port 8000
```

## Translation Engines

### Free Engines (No API Key)
- Google Translate (web scraping)
- Bing Translator (web scraping)
- MyMemory
- PONS Dictionary
- Linguee
- LibreTranslate

### Premium Engines (API Key Required)
- Google Gemini AI
- OpenAI GPT-4o
- DeepL Pro
- Microsoft Translator
- Baidu Translate
- Yandex Translate

Configure your API keys in the **Settings** page.

## Need Help?

- Check the [API Reference](api.md) for endpoint details
- Review [Usage Guide](usage.md) for examples
- See [Architecture](architecture.md) for system design
- Read [Development](development.md) for contributing

## License

This project is provided as-is for educational and personal use.
