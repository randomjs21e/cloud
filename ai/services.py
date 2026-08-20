import json
import urllib.request

from django.conf import settings

DEFAULT_SYSTEM_PROMPT = (
    "Sən CLX adlı süni intellekt köməkçisisən. "
    "İstifadəçilərə aydın, faydalı və Azərbaycan dilində cavab ver. "
    "Kod yazarkən təmiz və izahlı kod yaz. "
    "Sual aydın deyilsə, əlavə sual ver."
)


def get_ollama_models():
    """Fetch the list of available Ollama models. Returns (list, error)."""
    base_url = getattr(settings, 'AI_BASE_URL', 'http://localhost:11434')
    url = base_url.rstrip('/') + '/api/tags'
    req = urllib.request.Request(url, method='GET')
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        models = [m.get('name', '') for m in data.get('models', []) if m.get('name')]
        return models, None
    except Exception as e:
        return [], f'Ollama modelləri yüklənə bilmədi: {e}'


def get_ai_response(messages, model=None, system_prompt=None):
    """Call the configured LLM (Ollama local or OpenAI-compatible) and return the reply text.

    Returns (text, error) where error is None on success.
    """
    provider = getattr(settings, 'AI_PROVIDER', 'ollama')
    if provider == 'ollama':
        return _call_ollama(messages, model=model, system_prompt=system_prompt)
    return _call_openai_compatible(messages, model=model, system_prompt=system_prompt)


def _call_ollama(messages, model=None, system_prompt=None):
    base_url = getattr(settings, 'AI_BASE_URL', 'http://localhost:11434')
    model = model or getattr(settings, 'AI_MODEL', 'dolphincoder:latest')
    system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
    url = base_url.rstrip('/') + '/api/chat'

    payload = {
        'model': model,
        'messages': [{'role': 'system', 'content': system_prompt}] + messages,
        'stream': False,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return data.get('message', {}).get('content', ''), None
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        return None, f'Ollama xəta qaytardı ({e.code}): {body[:200]}'
    except Exception as e:
        return None, f'Ollama-ya qoşulmaq mümkün olmadı: {e}'


def _call_openai_compatible(messages, model=None, system_prompt=None):
    api_key = getattr(settings, 'AI_API_KEY', '')
    if not api_key:
        return None, 'AI açarı quraşdırılmayıb. Admin settings.py faylında AI_API_KEY təyin edin.'

    base_url = getattr(settings, 'AI_BASE_URL', 'https://api.abacus.ai/api/v1')
    model = model or getattr(settings, 'AI_MODEL', 'gpt-4o-mini')
    system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
    url = base_url.rstrip('/') + '/chat/completions'

    payload = {
        'model': model,
        'messages': [{'role': 'system', 'content': system_prompt}] + messages,
        'temperature': 0.7,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}',
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return data['choices'][0]['message']['content'], None
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        return None, f'AI xidməti xəta qaytardı ({e.code}): {body[:200]}'
    except Exception as e:
        return None, f'AI xidmətinə qoşulmaq mümkün olmadı: {e}'
