import copy, json, unittest
from pathlib import Path
from server import build
ROOT=Path(__file__).resolve().parent.parent
class Calculations(unittest.TestCase):
    def setUp(self): self.raw=json.loads((ROOT/'Growth_Institute_Dashboard_Data.json').read_text(encoding='utf-8-sig'))
    def test_snapshot(self):
        v=build(self.raw)
        self.assertEqual((v['active'],v['withdrawn'],v['enrolled'],v['week']),(11,1,12,6))
        self.assertEqual((v['completed'],v['opportunities'],v['percent']),(44,66,67))
        self.assertEqual([m['count'] for m in v['modules'][:6]],[10,10,8,7,7,2])
        self.assertEqual([s['count'] for s in v['sessions'][:6]],[11,10,9,6,6,5])
        self.assertEqual([s['eligible'] for s in v['sessions'][:6]],[12,12,12,11,11,11])
        self.assertEqual([s['averageMinutes'] for s in v['sessions'][:6]],[83.5,81.8,78.1,81.5,83.7,82.0])
        active=[p for p in v['people'] if p['status']=='active']
        self.assertEqual([sum(p['weekly'][i]['modules'] for p in active) for i in range(6)],[10,10,8,7,7,2])
        self.assertEqual([sum(p['weekly'][i]['sessions'] for p in active) for i in range(6)],[10,9,9,6,6,5])
        self.assertEqual([sum(bool(p['weekly'][i]['modules'] or p['weekly'][i]['sessions']) for p in active) for i in range(6)],[10,10,10,8,8,5])
        self.assertEqual(sum(p['weekly'][i]['modules'] for p in active for i in range(5)),42)
        self.assertEqual(sum(p['weekly'][i]['sessions'] for p in active for i in range(5)),40)
        self.assertTrue(all(p['completedWeeks']==5 for p in active))
        self.assertEqual(v['duplicateCompletions'],1)
        withdrawn=next(p for p in v['people'] if p['status']=='withdrawn')
        self.assertTrue(all(s['state']=='Not eligible' for s in withdrawn['sessions'][3:]))
    def test_duplicate_and_reconnect(self):
        before=build(self.raw)
        self.raw['completions'].append(copy.deepcopy(self.raw['completions'][0]))
        self.raw['attendance'].append(copy.deepcopy(self.raw['attendance'][0]))
        after=build(self.raw)
        self.assertEqual(before['completed'],after['completed'])
        self.assertEqual(before['sessions'],after['sessions'])
    def test_privacy_and_replaceability(self):
        self.raw['company']['sponsor']['email']='PRIVATE_SENTINEL'
        self.raw['learners'][0]['coachNotes']='PRIVATE_SENTINEL'
        self.raw['learners'][0]['name']='<script>replacement</script>'
        self.raw['company']['name']='Replacement company'
        view=build(self.raw); encoded=json.dumps(view)
        self.assertNotIn('PRIVATE_SENTINEL',encoded)
        self.assertEqual(view['company'],'Replacement company')
        self.assertEqual(view['people'][0]['name'],'<script>replacement</script>')
        html=(ROOT/'app'/'index.html').read_text(encoding='utf-8-sig')
        self.assertNotIn('innerHTML',html)
    def test_zero_and_partial_weeks(self):
        self.raw['learners']=[]; self.raw['completions']=[]; self.raw['attendance']=[]
        v=build(self.raw); self.assertIsNone(v['percent']);self.assertEqual(v['people'],[])
        self.assertEqual(v['opportunities'],0)
    def test_contradictions(self):
        self.raw['completions'][0]['completedAt']='not a date'
        with self.assertRaises(ValueError):build(self.raw)
    def test_no_positive_overlap(self):
        self.raw['attendance'][0]['leftAt']='2026-09-29T15:59:00.000Z'
        with self.assertRaises(ValueError):build(self.raw)
if __name__=='__main__':unittest.main(verbosity=2)
