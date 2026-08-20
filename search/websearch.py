import html
import re
import urllib.parse
import urllib.request

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36'


def search_web(query, num=10):
    """Search the web via DuckDuckGo HTML (no API key required).

    Returns (results, error). Each result: {title, url, snippet}.
    """
    url = 'https://html.duckduckgo.com/html/?q=' + urllib.parse.quote(query)
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            page = resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return [], f'İnternet axtarışı mümkün olmadı: {e}'

    results = []
    # Each result is in a <div class="result"> ... <a class="result__a" href="...">title</a>
    # snippet in <a class="result__snippet">
    blocks = re.split(r'<div class="result[^"]*">', page)
    for block in blocks[1:]:
        m = re.search(r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', block, re.S)
        if not m:
            continue
        href = html.unescape(m.group(1))
        title = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        # DuckDuckGo wraps real URL in uddg=... param
        real = _extract_real_url(href)
        snip_m = re.search(r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>', block, re.S)
        snippet = re.sub(r'<[^>]+>', '', snip_m.group(1)).strip() if snip_m else ''
        results.append({'title': title, 'url': real, 'snippet': snippet})
        if len(results) >= num:
            break

    if not results:
        return [], 'İnternetdə nəticə tapılmadı.'
    return results, None


def _extract_real_url(href):
    """DuckDuckGo result links contain the real URL in a uddg= query param."""
    if 'uddg=' in href:
        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
        if 'uddg' in parsed:
            return parsed['uddg'][0]
    return href
