# Paper Finder API Reference

Fallback reference for manual curl commands when the Python script is unavailable.

## Semantic Scholar

**Search:**
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=<keywords>&limit=20&fields=title,authors,year,citationCount,url,externalIds,abstract"
```

**Lookup by ArXiv ID:**
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/ArXiv:<arxiv_id>?fields=title,authors,year,citationCount,url,externalIds,abstract"
```

**Lookup by DOI:**
```bash
curl -s "https://api.semanticscholar.org/graph/v1/paper/DOI:<doi>?fields=title,authors,year,citationCount,url,externalIds,abstract"
```

**Rate Limit:** 100 requests / 5 minutes (no key). Free API key available at https://www.semanticscholar.org/product/api#api-key-form

**Response Fields:**
- `title` (string)
- `authors` (array of {name})
- `year` (int)
- `citationCount` (int)
- `url` (string) - Semantic Scholar page
- `externalIds` (object) - {ArXiv, DOI, PubMed, ...}
- `abstract` (string)

---

## OpenAlex

**Search:**
```bash
curl -s "https://api.openalex.org/works?search=<keywords>&per_page=20&select=title,authorships,publication_year,cited_by_count,doi,id"
```

**Lookup by DOI:**
```bash
curl -s "https://api.openalex.org/works/doi:<doi>"
```

**Rate Limit:** ~100,000 requests/day. Add `mailto=your@email.com` parameter for polite pool (faster).

**Response Fields:**
- `title` (string)
- `authorships` (array of {author: {display_name}})
- `publication_year` (int)
- `cited_by_count` (int)
- `doi` (string) - Full DOI URL
- `id` (string) - OpenAlex work ID

---

## ArXiv

**Search:**
```bash
curl -s "http://export.arxiv.org/api/query?search_query=all:<keywords>&start=0&max_results=20&sortBy=relevance&sortOrder=descending"
```

**Response:** Atom XML format. Key fields per `<entry>`:
- `<title>` - Paper title
- `<author><name>` - Author names
- `<published>` - Publication date (YYYY-MM-DDTHH:MM:SSZ)
- `<summary>` - Abstract
- `<id>` - ArXiv URL (contains ArXiv ID)
- `<link title="pdf" href="...">` - PDF link

**Rate Limit:** 3 requests/second. No API key needed.

**Search Query Syntax:**
- `all:` - All fields
- `ti:` - Title only
- `au:` - Author only
- `abs:` - Abstract only
- Boolean: `AND`, `OR`, `ANDNOT`
- Example: `ti:transformer AND abs:attention`

