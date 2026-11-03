import copy, json, unittest, threading, urllib.request, urllib.error
from pathlib import Path
from unittest.mock import patch
from http.server import HTTPServer
from server import build, Handler
from access import Access, password_hash
ROOT=Path(__file__).resolve().parent.parent
class Boundaries(unittest.TestCase):
    def setUp(self): self.raw=json.loads((ROOT/'Growth_Institute_Dashboard_Data.json').read_text(encoding='utf-8-sig'))
    def test_all_learners_have_complete_details(self):
        for p in build(self.raw)['people']:
            self.assertEqual(len(p['modules']),8)
            self.assertEqual(len(p['sessions']),8)
            self.assertEqual(len(p['weekly']),8)
            for s in p['sessions']:
                self.assertIn('minutes',s)
                if s['state']=='Joined': self.assertGreater(s['minutes'],0);self.assertLessEqual(s['minutes'],90)
                else:self.assertIsNone(s['minutes'])
    def test_release_context_moves_with_dates(self):
        view=build(self.raw)
        self.assertEqual([m['order'] for m in view['modules'] if m['currentWeek']],[6])
        self.raw['generatedAt']='2026-11-10T19:13:00.151Z'
        self.assertEqual([m['order'] for m in build(self.raw)['modules'] if m['currentWeek']],[7])
    def test_overlap_union_and_duration_clipping(self):
        self.raw['attendance']=[{'learnerId':'lrn_01','sessionId':'ses_01','joinedAt':a,'leftAt':b} for a,b in [('2026-09-29T15:40:00Z','2026-09-29T16:40:00Z'),('2026-09-29T16:20:00Z','2026-09-29T17:50:00Z')]]
        v=build(self.raw); s=v['sessions'][0]
        self.assertEqual((s['count'],s['measuredAttendees'],s['averageMinutes']),(1,1,90))
    def test_disjoint_reconnects(self):
        self.raw['attendance']=[{'learnerId':'lrn_01','sessionId':'ses_01','joinedAt':a,'leftAt':b} for a,b in [('2026-09-29T16:00:00Z','2026-09-29T16:10:00Z'),('2026-09-29T16:30:00Z','2026-09-29T16:45:00Z')]]
        self.assertEqual(build(self.raw)['sessions'][0]['averageMinutes'],25)
    def test_in_progress_and_no_completed_weeks(self):
        self.raw['learners']=[l for l in self.raw['learners'] if l['status']=='active'];self.raw['generatedAt']='2026-09-29T16:30:00Z';self.raw['completions']=[]
        self.raw['attendance']=[self.raw['attendance'][1]]
        v=build(self.raw);p=v['people'][0]
        self.assertEqual(v['sessions'][0]['state'],'In progress')
        self.assertEqual(p['sessionEligible'],0);self.assertEqual(p['joined'],0)
        self.assertEqual(p['sessions'][0]['minutes'],30)
        self.assertEqual(p['completedWeeks'],0);self.assertIsNone(p['averageModules']);self.assertIsNone(p['averageSessions'])
        self.assertEqual(v['opportunities'],11)
    def test_no_releases_no_attendees(self):
        self.raw['learners']=[l for l in self.raw['learners'] if l['status']=='active'];self.raw['generatedAt']='2026-09-27T00:00:00Z';self.raw['completions']=[];self.raw['attendance']=[]
        v=build(self.raw);self.assertEqual(v['opportunities'],0);self.assertIsNone(v['percent'])
        self.assertIsNone(v['sessions'][0]['averageMinutes']);self.assertEqual(v['sessions'][0]['measuredAttendees'],0)
    def test_earliest_completion_retained(self):
        self.raw['completions'].append({'learnerId':'lrn_01','moduleId':'mod_01','completedAt':'2026-09-29T12:00:00Z'})
        p=build(self.raw)['people'][0]
        self.assertEqual(p['completed'],6);self.assertEqual(p['modules'][0]['completedAt'],'2026-09-29T12:00:00Z')
    def test_invalid_records_are_rejected(self):
        cases=[]
        r=copy.deepcopy(self.raw);r['learners'][0]['withdrawnAt']={'private':'secret'};cases.append(r)
        r=copy.deepcopy(self.raw);r['learners'][0]['enrolledAt']='2026-10-01T00:00:00Z';cases.append(r)
        r=copy.deepcopy(self.raw);r['sessions'][0]['week']=2;cases.append(r)
        r=copy.deepcopy(self.raw);r['learners'].append(r['learners'][0]);cases.append(r)
        r=copy.deepcopy(self.raw);del r['attendance'][0]['leftAt'];cases.append(r)
        r=copy.deepcopy(self.raw);r['completions'][0]['completedAt']='2026-09-27T00:00:00Z';cases.append(r)
        r=copy.deepcopy(self.raw);r['attendance'].append({'learnerId':'lrn_08','sessionId':'ses_04','joinedAt':'2026-10-20T16:00:00Z','leftAt':'2026-10-20T17:00:00Z'});cases.append(r)
        for r in cases:
            with self.subTest(case=cases.index(r)):
                with self.assertRaises((ValueError,KeyError,TypeError)):build(r)
    def test_private_fields_at_every_record_level(self):
        private=['coachNotes','email','sponsorEmail','joinUrl','recordingUrl','minutesSpent','studyTimeEstimate','timezone','industry','headcount','coachName','description']
        targets=[self.raw,self.raw['company'],self.raw['company']['sponsor'],self.raw['program']]
        for k in ['learners','modules','sessions','completions','attendance']:targets+=self.raw[k]
        for obj in targets:
            for key in private:obj[key]='PRIVATE_SENTINEL'
        encoded=json.dumps(build(self.raw))
        self.assertNotIn('PRIVATE_SENTINEL',encoded)
        for key in private:self.assertNotIn('"'+key+'":',encoded)

class HttpBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http=HTTPServer(('127.0.0.1',0),Handler);cls.http.access=Access({'username':'sponsor','salt':'ab'*16,'passwordHash':password_hash('test-password','ab'*16),'companyId':'cmp_northwind','programId':'prg_scaleup_os'});cls.cookie='gi_session='+cls.http.access.issue();cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start();cls.base='http://127.0.0.1:'+str(cls.http.server_port)
    @classmethod
    def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.thread.join()
    def request(self,path):
        try:
            with urllib.request.urlopen(urllib.request.Request(self.base+path,headers={'Cookie':self.cookie})) as r:return r.status,r.read().decode('utf-8-sig')
        except urllib.error.HTTPError as e:return e.code,e.read().decode('utf-8')
    def test_route_denial_and_query_cannot_select_scope(self):
        for path in ['/Growth_Institute_Dashboard_Data.json','/app/server.py','/../README.md','/%2e%2e/README.md','/.git/config']:
            self.assertEqual(self.request(path)[0],404)
        code,body=self.request('/api/dashboard?companyId=another&programId=another')
        self.assertEqual(code,200);self.assertEqual(json.loads(body)['company'],'Northwind Logistics')
    def test_company_and_program_scope_rejected_server_side(self):
        source=json.loads((ROOT/'Growth_Institute_Dashboard_Data.json').read_text(encoding='utf-8-sig'))
        for field in ['company','program']:
            changed=copy.deepcopy(source);changed[field]['id']='other_scope'
            with patch.object(Path,'read_text',return_value=json.dumps(changed)):
                code,body=self.request('/api/dashboard?companyId=cmp_northwind')
            self.assertEqual(code,403);self.assertNotIn('people',body)
    def test_invalid_missing_empty_and_private_source(self):
        with patch.object(Path,'read_text',return_value='{broken'):
            self.assertEqual(self.request('/api/dashboard')[0],422)
        with patch.object(Path,'read_text',side_effect=FileNotFoundError('PRIVATE_SENTINEL')):
            code,body=self.request('/api/dashboard');self.assertEqual(code,422);self.assertNotIn('PRIVATE_SENTINEL',body)
        raw=json.loads((ROOT/'Growth_Institute_Dashboard_Data.json').read_text(encoding='utf-8-sig'))
        raw['learners'][0]['coachNotes']='PRIVATE_SENTINEL';raw['company']['sponsor']['email']='PRIVATE_SENTINEL'
        with patch.object(Path,'read_text',return_value=json.dumps(raw)):
            code,body=self.request('/api/dashboard');self.assertEqual(code,200);self.assertNotIn('PRIVATE_SENTINEL',body)
        raw['learners']=[];raw['completions']=[];raw['attendance']=[]
        with patch.object(Path,'read_text',return_value=json.dumps(raw)):
            code,body=self.request('/api/dashboard');self.assertEqual(code,200);self.assertEqual(json.loads(body)['people'],[])
if __name__=='__main__':unittest.main(verbosity=2)

