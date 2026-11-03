"""Small local sponsor access boundary, deliberately independent of learner identity."""
import json, secrets, hashlib, hmac, time, threading
from pathlib import Path
from http.cookies import SimpleCookie
ROOT=Path(__file__).resolve().parent.parent
def load_config():
    config=json.loads((ROOT/'.local-config.json').read_text())
    if len(config['passwordHash'])!=64 or len(config['salt'])<32:raise ValueError('Invalid local configuration')
    return config
def password_hash(password,salt):return hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),600000).hex()
def session_token(headers):
    try:
        cookie=SimpleCookie();cookie.load(headers.get('Cookie',''));return cookie['gi_session'].value if 'gi_session' in cookie else ''
    except Exception:return ''
class Access:
    def __init__(self,config):
        self.config=config;self.company=config['companyId'];self.program=config['programId'];self.sessions={};self.failures={};self.lock=threading.Lock()
    def login(self,username,password,address):
        now=time.monotonic()
        with self.lock:
            self.failures={k:[t for t in times if now-t<60] for k,times in self.failures.items() if any(now-t<60 for t in times)}
            attempts=self.failures.setdefault(address,[])
            if len(attempts)>=5:return 'limited'
            # Charge attempts before expensive hashing, also bounding parallel attempts.
            attempts.append(now)
        valid=hmac.compare_digest(password_hash(password,self.config['salt']),self.config['passwordHash']) and hmac.compare_digest(username.encode('utf-8'),self.config['username'].encode('utf-8'))
        if not valid:return None
        return self.issue()
    def issue(self):
        token=secrets.token_urlsafe(32)
        with self.lock:
            now=time.monotonic();self.sessions={k:v for k,v in self.sessions.items() if v>now};self.sessions[token]=now+3600
        return token
    def authorized(self,token):
        with self.lock:return bool(token) and self.sessions.get(token,0)>time.monotonic()
    def logout(self,token):
        with self.lock:self.sessions.pop(token,None)
    def cookie(self,token,expired=False):
        # HTTP-only loopback demo; Secure must be enabled behind HTTPS in a deployment.
        return 'gi_session='+token+'; Path=/; HttpOnly; SameSite=Strict; Max-Age='+('0' if expired else '3600')
def login_page(error=''):
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sponsor sign-in · Growth Institute</title><style>body{background:#190e30;color:#faf7ff;font:16px/1.5 system-ui;padding:24px}main{max-width:400px;margin:10vh auto;background:#342151;padding:30px;border-radius:20px}label,input,button{display:block;box-sizing:border-box;width:100%}input,button{font:inherit;margin:8px 0 20px;padding:12px;border-radius:8px;border:1px solid #c4a5f4}button{background:#c4a5f4;color:#190e30;cursor:pointer}p{color:#c3b6d5}:focus-visible{outline:3px solid white;outline-offset:3px}</style><main><h1>Sponsor sign-in</h1><p>Growth Institute · Company program overview</p><p>This local challenge demo uses a provisioned sponsor account. Learners do not have sponsor access.</p><p role="status">'''+error+'''</p><form method="post" action="/login"><label for="username">Username</label><input id="username" name="username" autocomplete="username" required maxlength="100"><label for="password">Password</label><input id="password" name="password" type="password" autocomplete="current-password" required maxlength="200"><button>Sign in</button></form></main></html>'''

