import copy, json, time, unittest, threading, urllib.request, urllib.error, urllib.parse
from pathlib import Path
from http.server import HTTPServer
from unittest.mock import patch
from access import Access, password_hash
from server import Handler, build
import source
ROOT=Path(__file__).resolve().parent.parent
CONFIG={'username':'sponsor','salt':'ab'*16,'passwordHash':password_hash('test-password-123','ab'*16),'companyId':'cmp_northwind','programId':'prg_scaleup_os'}
class AccessTests(unittest.TestCase):
    def setUp(self):
        self.http=HTTPServer(('127.0.0.1',0),Handler);self.http.access=Access(CONFIG);self.thread=threading.Thread(target=self.http.serve_forever,daemon=True);self.thread.start();self.base='http://127.0.0.1:'+str(self.http.server_port)
    def tearDown(self):self.http.shutdown();self.http.server_close();self.thread.join()
    def request(self,path,values=None,cookie='',origin=True):
        headers={'Cookie':cookie}
        if values is not None:headers['Content-Type']='application/x-www-form-urlencoded'
        if origin:headers['Origin']=self.base
        req=urllib.request.Request(self.base+path,headers=headers,data=urllib.parse.urlencode(values).encode() if values is not None else None)
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self,*args):return None
        try:
            with urllib.request.build_opener(NoRedirect).open(req) as r:return r.status,r.headers,r.read().decode()
        except urllib.error.HTTPError as e:return e.code,e.headers,e.read().decode()
    def test_anonymous_and_forged_access_denied(self):
        self.assertEqual(self.request('/api/dashboard')[0],401)
        self.assertEqual(self.request('/api/dashboard?companyId=cmp_northwind',cookie='gi_session=forged')[0],401)
        code,h,b=self.request('/');self.assertEqual(code,303);self.assertEqual(h['Location'],'/login')
        self.assertEqual(self.request('/login')[0],200)
    def test_login_logout_cookie_scope_and_expiry(self):
        code,h,b=self.request('/login',{'username':'sponsor','password':'test-password-123'})
        self.assertEqual(code,303);cookie=h['Set-Cookie'];self.assertIn('HttpOnly',cookie);self.assertIn('SameSite=Strict',cookie)
        cookie=cookie.split(';')[0]
        self.assertEqual(self.request('/api/dashboard',cookie=cookie)[0],200)
        self.assertEqual(self.request('/logout',{},cookie=cookie)[0],303)
        self.assertEqual(self.request('/api/dashboard',cookie=cookie)[0],401)
        token=self.http.access.issue();self.http.access.sessions[token]=time.monotonic()-1
        self.assertEqual(self.request('/api/dashboard',cookie='gi_session='+token)[0],401)
    def test_wrong_password_rate_limit_and_cross_origin(self):
        self.assertEqual(self.request('/login',{'username':'sponsor','password':'wrong'},origin=False)[0],403)
        for i in range(5):self.assertEqual(self.request('/login',{'username':'learner','password':'wrong'})[0],401)
        self.assertEqual(self.request('/login',{'username':'sponsor','password':'test-password-123'})[0],429)
class SourceTests(unittest.TestCase):
    def setUp(self):source._cache=None;source._until=0
    def test_projection_and_cache(self):
        raw=json.loads((ROOT/'Growth_Institute_Dashboard_Data.json').read_text(encoding='utf-8-sig'));raw['learners'][0]['coachNotes']='PRIVATE_SENTINEL'
        class Response:
            def __enter__(self):return self
            def __exit__(self,*a):pass
            def geturl(self):return source.URL
            def read(self,n):return json.dumps(raw).encode()
        with patch.object(source,'urlopen',return_value=Response()) as mock:
            safe=source.load_source('live');self.assertNotIn('PRIVATE_SENTINEL',json.dumps(safe));source.load_source('live');self.assertEqual(mock.call_count,1)
        self.assertEqual(build(safe)['completed'],44)
    def test_failure_has_no_fixture_fallback(self):
        with patch.object(source,'urlopen',side_effect=OSError('PRIVATE_SENTINEL')):
            with self.assertRaises(source.SourceError) as result:source.load_source('live')
        self.assertNotIn('PRIVATE_SENTINEL',str(result.exception))
class ScaleTests(unittest.TestCase):
    def test_ten_times_dataset(self):
        raw=json.loads((ROOT/'Growth_Institute_Dashboard_Data.json').read_text(encoding='utf-8-sig'))
        large=copy.deepcopy(raw);large['learners']=[];large['completions']=[];large['attendance']=[]
        for i in range(10):
            suffix='_'+str(i)
            for l in raw['learners']:
                c=copy.deepcopy(l);c['id']+=suffix;c['name']+=' '+str(i);large['learners'].append(c)
            for key in ['completions','attendance']:
                for record in raw[key]:
                    c=copy.deepcopy(record);c['learnerId']+=suffix;large[key].append(c)
        start=time.perf_counter();v=build(large);elapsed=time.perf_counter()-start
        self.assertEqual((v['enrolled'],v['active'],v['completed'],v['opportunities']),(120,110,440,660))
        self.assertEqual([s['count'] for s in v['sessions'][:6]],[110,100,90,60,60,50])
        self.assertEqual(len(v['people']),120)
        print('120-learner calculation: %.4fs; sponsor response: %s bytes'%(elapsed,len(json.dumps(v).encode())))
        # Record an observation, not an unstable machine-speed pass/fail threshold.
if __name__=='__main__':unittest.main(verbosity=2)
