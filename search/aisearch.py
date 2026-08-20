import json
import urllib.request

from django.conf import settings


def ask_ai(question, context=None):
    """Ask the local Ollama model a question, optionally with web context.

    Returns (text, error).
    """
    base_url = getattr(settings, 'AI_BASE_URL', 'http://localhost:11434')
    model = getattr(settings, 'AI_MODEL', 'dolphincoder:latest')
    url = base_url.rstrip('/') + '/api/chat'

    system = (
        "Sən CLX axtarış köməkçisisən. İstifadəçinin sualına aydın və Azərbaycan dilində cavab ver. "
        "Əgər internet nəticələri verilibsə, onlardan istifadə edərək qısa və faydalı cavab yaz. "
        "Mənbələri qeyd et."
    )
    messages = [{'role': 'system', 'content': system}]
    if context:
        messages.append({'role': 'system', 'content': 'İnternet nəticələri:\n' + context})
    messages.append({'role': 'user', 'content': question})

    payload = {'model': model, 'messages': messages, 'stream': False}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return data.get('message', {}).get('content', ''), None
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        return None, f'Ollama xəta qaytardı ({e.code}): {body[:200]}'
    except Exception as e:
        return None, f'Ollama-ya qoşulmaq mümkün olmadı: {e}'
