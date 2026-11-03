"""Read-only challenge adapter; raw external records never reach the browser or disk."""
import json, time, threading
from urllib.request import urlopen, Request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
URL='https://jobs.growthinstitute.com/api/challenge/all'
class SourceError(Exception):pass
FIELDS={'program':['id','name','weeks','startsAt','endsAt'],'company':['id','name'],'learners':['id','name','title','status','enrolledAt','withdrawnAt'],'modules':['id','order','title','releasedAt'],'completions':['learnerId','moduleId','completedAt'],'sessions':['id','week','moduleId','title','scheduledAt','durationMinutes'],'attendance':['sessionId','learnerId','joinedAt','leftAt']}
def project(raw):
    def keep(row,fields):return {k:row[k] for k in fields if k in row}
    result={'schemaVersion':'1.0','dataKind':'fictional-challenge-data','generatedAt':raw['generatedAt']}
    for key,fields in FIELDS.items():
        result[key]=keep(raw[key],fields) if key in ('program','company') else [keep(row,fields) for row in raw[key]]
    result['company']['sponsor']=keep(raw['company']['sponsor'],['name','title'])
    return result
_cache=None
_until=0
_lock=threading.Lock()
def load_source(mode):
    if mode=='fixture':return json.loads((ROOT/'Growth_Institute_Dashboard_Data.json').read_text(encoding='utf-8-sig'))
    if mode!='live':raise ValueError('Unknown source mode')
    global _cache,_until
    with _lock:
        if _cache is not None and time.monotonic()<_until:return _cache
        try:
            with urlopen(Request(URL,headers={'Accept':'application/json','User-Agent':'GrowthInstituteSponsorChallenge/1.0'}),timeout=15) as response:
                if response.geturl()!=URL:raise ValueError('Unexpected redirect')
                payload=response.read(2_000_001)
                if len(payload)>2_000_000:raise ValueError('Response too large')
                safe=project(json.loads(payload))
        except Exception as error:
            # No raw data, URL parameters or private exception details in client errors.
            raise SourceError('Challenge source unavailable') from None
        _cache=safe;_until=time.monotonic()+60
        return safe
