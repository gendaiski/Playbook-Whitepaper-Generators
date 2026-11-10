"""Personal HTTPS link access; no ChatGPT or third-party login required."""
import hashlib
import hmac
import json
import os
from http.cookies import SimpleCookie, CookieError

ACCESS_TOKEN = os.environ.get('OPENDRAFT_ACCESS_TOKEN', '')
if ACCESS_TOKEN and len(ACCESS_TOKEN) < 32:
    raise RuntimeError('OPENDRAFT_ACCESS_TOKEN must contain at least 32 random characters')


def enabled():
    return bool(ACCESS_TOKEN)


def cookie_value():
    return hmac.new(ACCESS_TOKEN.encode(), b'opendraft-personal-session-v1', hashlib.sha256).hexdigest()


def authorized(headers):
    if not enabled():
        return True
    try:
        cookie = SimpleCookie(headers.get('Cookie', ''))
        value = cookie.get('od_session')
        return bool(value and hmac.compare_digest(value.value, cookie_value()))
    except (CookieError, TypeError):
        return False


def unlock(handler):
    """Receive the fragment token over HTTPS and issue an HttpOnly session cookie."""
    try:
        size = int(handler.headers.get('Content-Length', '0'))
        if size < 1 or size > 2048:
            raise ValueError('Invalid request')
        data = json.loads(handler.rfile.read(size))
        valid = enabled() and hmac.compare_digest(str(data.get('token', '')), ACCESS_TOKEN)
    except (ValueError, TypeError, AttributeError):
        valid = False
    body = b'{"ok":true}' if valid else b'{"error":"Use your personal preview link to enter."}'
    handler.send_response(200 if valid else 403)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Content-Length', str(len(body)))
    handler.send_header('Cache-Control', 'no-store')
    handler.send_header('Referrer-Policy', 'no-referrer')
    if valid:
        handler.send_header('Set-Cookie', 'od_session=' + cookie_value() + '; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=86400')
    handler.end_headers()
    handler.wfile.write(body)


ENTRY_HTML = b'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><title>OpenDraft</title><style>body{margin:0;background:#f5f3ed;color:#18344d;font:17px/1.6 system-ui;display:grid;place-items:center;min-height:100vh}main{max-width:520px;padding:36px}h1{font:44px Georgia}small{color:#5b6d7a}</style><main><h1>OpenDraft.</h1><p id="message">Opening your research workspace...</p><small>No ChatGPT account required.</small></main><script>
(async()=>{
const token=new URLSearchParams(location.hash.slice(1)).get('access');
if(!token){document.querySelector('#message').textContent='Open the personal preview link supplied in your chat to enter this workspace.';return;}
history.replaceState(null,'',location.pathname);
try{const r=await fetch('/api/unlock',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({token})});if(!r.ok)throw Error('This preview link is no longer valid.');location.replace('/');}catch(e){document.querySelector('#message').textContent=e.message;}
})();</script></html>'''
