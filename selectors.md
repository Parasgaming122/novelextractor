# Selectors Documentation

This document records all CSS selectors, HTML tags, and attributes used by the universal novel scraper for each supported source.

## Source: ixdzs8 (https://ixdzs8.com)

### Feed (`/hot/day/`)
| Field | Selector | Tag/Attribute | Notes |
|-------|----------|---------------|-------|
| Item Container | `.burl, .u-list li, .book-item` | `li` or `div` | Multiple fallback selectors |
| Title | `h3 a, h2 a, .title a, .bname a` | `a` tag | Text content |
| URL | Same as title | `href` attribute | Relative URL |
| Author | `.author, .book-author, .bauthor a` | `a` or text | Text content |
| Description | `.desc, .description, .intro, .l-p2` | Text | May be truncated |
| Cover Image | `img` | `src` or `data-src` attribute | Use urljoin for absolute URL |
| Rating | `.rating, .score, .stars` | Text | Optional field |

### Search (`/bsearch?q={query}`)
| Field | Selector | Tag/Attribute | Notes |
|-------|----------|---------------|-------|
| Item Container | `.u-list li, .book-item, .search-result` | `li` or `div` | |
| Title | `h3 a, h2 a, .title a` | `a` tag | |
| Author | `.author, .book-author` | Text | |
| Description | `.desc, .description, .intro` | Text | |
| Cover | `img` | `src` or `data-src` | |

---

## Source: xbiquge (https://www.xbiquge.info)

### Feed (`/top/week_0_1.html`)
| Field | Selector | Tag/Attribute | Notes |
|-------|----------|---------------|-------|
| Item Container | `dl` | `dl` tag | Each novel is in a dl element |
| Title | `h3 a` inside `dd` | `a` tag | Text content |
| URL | Same as title | `href` attribute | Pattern: `/XX/XXXXX/` |
| Cover Image | `dt img` | `src` attribute | Relative URL, use urljoin |
| Author | `.book_other a` (second dd with class) | `a` tag | After "作者：" text |
| Status | `.book_other` (third dd) | Text | After "状态：" |
| Latest Chapter | `.book_other a` (last dd) | `a` tag | After "最新章节：" |
| Update Time | `.book_other` (fourth dd) | Text | After "更新时间：" |

### Search (`/search.php?q={query}`)
| Field | Selector | Tag/Attribute | Notes |
|-------|----------|---------------|-------|
| Item Container | `#maincontent tr, .grid tr` | `tr` tag | Table row format |
| Title | First `td a` | `a` tag | |
| Author | Second `td` | Text | |
| Status | Third `td` | Text | |
| Latest Chapter | Fourth `td a` | `a` tag | |

**⚠️ ISSUE:** Current code uses `#maincontent tr` but feed page uses `dl` structure instead.

---

## Source: biquge.company (https://www.biquge.company)

### Feed (`/sort/0/1.html`)
| Field | Selector | Tag/Attribute | Notes |
|-------|----------|---------------|-------|
| Item Container | `.bookbox, .bookinfo` | `div` | |
| Title | `.bookname a` | `a` tag | |
| URL | Same as title | `href` attribute | Pattern: `/book/XXXXX.html` |
| Author | `.author` | Text | Remove "作者：" prefix |
| Latest Chapter | `.cat a` | `a` tag | |
| Description | `.update` | Text | |
| Cover Image | `img` | `src` attribute | |

### Search (POST to `/modules/article/search.php`)
| Field | Selector | Tag/Attribute | Notes |
|-------|----------|---------------|-------|
| Item Container | `.bookbox, .bookinfo` | `div` | |
| Title | `.bookname a` | `a` tag | |
| Author | `.author` | Text | |

**⚠️ ISSUE:** Feed returns duplicate entries. Need deduplication logic.

---

## Source: ttkan (https://www.ttkan.co)

### Feed (`/novel/rank`)
| Field | Selector | Tag/Attribute | Notes |
|-------|----------|---------------|-------|
| Item Container | `.rank_list .pure-u-xl-1-5, .pure-u-lg-1-4, .pure-u-md-1-3` | `div` | AMP-based layout |
| Title | `amp-img` or `img` | `alt` attribute | NOT from h2/a tag text |
| URL | Parent `a` tag | `href` attribute | Pattern: `/novel/chapters/XXX` |
| Cover Image | `amp-img` or `img` | `src` attribute | Absolute URL from static.ttkan.co |

**⚠️ ISSUE:** Current code looks for text in h2/a tags but title is in `amp-img alt` attribute.

### Search (`/novel/search?q={query}`)
| Field | Selector | Tag/Attribute | Notes |
|-------|----------|---------------|-------|
| Item Container | `.novel_cell, [data-v-2ba0104b] .pure-g > div` | `div` | Vue.js based |
| Title | `a[href*='/novels/'], a[href*='/novel/'], h3 a, .title a` | `a` tag | |
| Author | `.author, .author-name` | Text | |
| Cover | `img` | `src` or `data-src` | |

---

## Source: shuhaige (https://m.shuhaige.net / https://shuhaige.net)

### Feed (`/shuku/` or `/shuku/0_0_0_1.html`)
| Field | Selector | Tag/Attribute | Notes |
|-------|----------|---------------|-------|
| Item Container | `.list li` | `li` tag | Inside `.library .list` ul |
| Title | `p.bookname a` | `a` tag | Text content |
| URL | Same as title | `href` attribute | Pattern: `/XXXXXX/` (mobile URL) |
| Cover Image | `img` (first child of li) | `src` attribute | Absolute URL from img.shuhaige.net |
| Author | `.data a.layui-btn-xs` | `a` tag | First button-style link in data p |
| Category | `.data span.layui-btn-radius` (first) | `span` | Genre/category |
| Status | `.data span.layui-btn-danger` or `.layui-btn-normal` | `span` | 完结/连载 |
| Description | `p.intro` | Text | Novel introduction |
| Latest Chapter | `.data a` (last link) | `a` tag | After "最新：" |

### Search (POST to `/search.html`)
| Field | Selector | Tag/Attribute | Notes |
|-------|----------|---------------|-------|
| Item Container | `.list li, .book-item` | `li` tag | Same structure as feed |
| Title | `p.bookname a` | `a` tag | |
| Author | `.data a` | `a` tag | |

**⚠️ ISSUE:** Current code only extracts title and cover_url, missing author, status, description fields.

---

## Common Patterns

### URL Patterns
| Source | Novel URL Pattern | Chapter URL Pattern |
|--------|------------------|---------------------|
| ixdzs8 | `/read/{id}/` | `/read/{id}/p{page}.html` |
| xbiquge | `/{XX}/{XXXXX}/` | `/{XX}/{XXXXX}/{chapter_id}.html` |
| biquge.company | `/book/{id}.html` | `/book/{id}/{chapter_num}.html` |
| ttkan | `/novel/chapters/{slug}-{author}` | `/novel/chapters/{slug}-{author}/{chapter}` |
| shuhaige | `/{id}/` (mobile) | `/{id}/{chapter_id}.html` |

### Image URL Patterns
| Source | Image Domain | Notes |
|--------|-------------|-------|
| ixdzs8 | `https://img22.ixdzs.com/` | Format: `/{folder}/{hash}.jpg` |
| xbiquge | Relative to domain | `/images/{id}/{id}s.jpg` |
| biquge.company | Relative to domain | Often empty on list pages |
| ttkan | `https://static.ttkan.co/cover/` | `{slug}-{author}.jpg` |
| shuhaige | `https://img.shuhaige.net/` | `/{id}/{image_id}.jpg` |

---

## Known Issues & Fixes Needed

### 1. xbiquge Feed Parser
**Problem:** Uses wrong selector (`#maincontent tr`) but actual structure is `dl > dt/dd`
**Fix:** Change parser to look for `dl` tags and extract from `dt` (cover) and `dd` (other info)

### 2. ttkan Feed Parser  
**Problem:** Title extraction fails because it looks for text in h2/a tags but title is in `amp-img alt` attribute
**Fix:** Extract title from `amp-img` or `img` tag's `alt` attribute

### 3. shuhaige Feed Parser
**Problem:** Only extracts title and cover_url, missing author, category, status, description
**Fix:** Add extraction for `.data` paragraph children elements

### 4. biquge.company Duplicates
**Problem:** Feed returns duplicate entries
**Fix:** Add deduplication by URL or title before returning results

### 5. biquge vs biquge_company naming
**Problem:** Usage docs reference `biquge` but source ID is `biquge_company`
**Fix:** Either rename source ID or add alias support

---

## Testing Commands

```bash
# Test each feed source
python3 universal_novel_scraper.py feed ixdzs8 --json
python3 universal_novel_scraper.py feed xbiquge --json
python3 universal_novel_scraper.py feed biquge_company --json
python3 universal_novel_scraper.py feed ttkan --json
python3 universal_novel_scraper.py feed shuhaige --json

# Get raw HTML for debugging
python3 -c "from bypasser import Bypasser; b = Bypasser(); print(b.fetch('URL_HERE')[:2000])"
```

---

## Last Updated
Date: 2024
Status: Documented all 5 sources with known issues identified
