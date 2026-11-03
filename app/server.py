"""File-backed sponsor demonstration. Python standard library only."""
import json, math
from pathlib import Path
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from source import load_source, SourceError
from access import Access, load_config, login_page, session_token
from urllib.parse import parse_qs, urlsplit
import argparse, time
ROOT = Path(__file__).resolve().parent.parent
DAY = timedelta(days=1)
def dt(v):
    if not isinstance(v, str) or not v.endswith('Z'): raise ValueError('Expected an ISO UTC timestamp')
    return datetime.fromisoformat(v.replace('Z','+00:00'))
def stamp(v): return v.isoformat().replace('+00:00','Z')
def build(raw):
    if raw.get('schemaVersion') != '1.0': raise ValueError('Unsupported schema version')
    now=dt(raw['generatedAt']); p=raw['program']; start=dt(p['startsAt']); end=dt(p['endsAt'])
    if not isinstance(p['weeks'],int) or p['weeks']<1 or end<=start: raise ValueError('Invalid program dates or weeks')
    def text(v):
        if not isinstance(v,str) or len(v)>500: raise ValueError('Invalid text field')
        return v
    def records(key):
        rows=raw[key]
        if not isinstance(rows,list): raise ValueError('Expected record list')
        if any(not isinstance(r,dict) or not isinstance(r.get('id'),str) or not r['id'] or len(r['id'])>100 for r in rows): raise ValueError('Invalid record ID')
        if len({r['id'] for r in rows})!=len(rows): raise ValueError('Duplicate IDs in '+key)
        return rows
    learners=records('learners'); modules=sorted(records('modules'),key=lambda m:m['order']); sessions=sorted(records('sessions'),key=lambda s:dt(s['scheduledAt']))
    lm={l['id']:l for l in learners}; mm={m['id']:m for m in modules}; sm={s['id']:s for s in sessions}
    for l in learners:
        text(l['name']); text(l['title']); enrolled=dt(l['enrolledAt'])
        if enrolled>start: raise ValueError('Late enrollment requires a module eligibility policy')
        if l['status']=='active' and 'withdrawnAt' in l: raise ValueError('Active learner has withdrawal date')
        if l['status'] not in ('active','withdrawn'): raise ValueError('Invalid learner status')
        if l['status']=='withdrawn' and dt(l['withdrawnAt'])<enrolled: raise ValueError('Withdrawal precedes enrollment')
        if l['status']=='withdrawn' and dt(l['withdrawnAt'])>now: raise ValueError('Withdrawal is after snapshot')
    for m in modules:
        text(m['title']); dt(m['releasedAt'])
        if type(m['order']) is not int or m['order']<1: raise ValueError('Invalid module order')
    if len({m['order'] for m in modules})!=len(modules): raise ValueError('Duplicate module order')
    for s in sessions:
        text(s['title'])
        if type(s['week']) is not int or s['week']!=(dt(s['scheduledAt'])-start).days//7+1 or not 1<=s['week']<=p['weeks']: raise ValueError('Session week contradicts program dates')
        if s['moduleId'] not in mm or not isinstance(s['durationMinutes'],(int,float)) or not 0<s['durationMinutes']<1440: raise ValueError('Invalid session')
    def eligible(l,t): return dt(l['enrolledAt'])<=t and (l['status']=='active' or t<dt(l['withdrawnAt']))
    def se(s): return dt(s['scheduledAt'])+timedelta(minutes=s['durationMinutes'])
    completed={}; duplicate=0
    for c in raw['completions']:
        l=lm[c['learnerId']]; m=mm[c['moduleId']]; t=dt(c['completedAt'])
        if t<dt(m['releasedAt']) or not eligible(l,t): raise ValueError('Contradictory completion')
        if t>now: raise ValueError('Completion is after snapshot')
        key=(l['id'],m['id'])
        if key in completed: duplicate+=1
        completed[key]=min(t,completed.get(key,t))
    intervals={}
    for a in raw['attendance']:
        l=lm[a['learnerId']]; s=sm[a['sessionId']]; begin=dt(a['joinedAt']); finish=dt(a['leftAt'])
        if finish<=begin or not eligible(l,dt(s['scheduledAt'])) or begin>now: raise ValueError('Contradictory attendance')
        lo=max(begin,dt(s['scheduledAt']),dt(l['enrolledAt'])); hi=min(finish,se(s),now)
        if l['status']=='withdrawn': hi=min(hi,dt(l['withdrawnAt']))
        if hi<=lo: raise ValueError('Attendance has no positive scheduled overlap')
        intervals.setdefault((l['id'],s['id']),[]).append((lo,hi))
    joined={}
    for key,parts in intervals.items():
        merged=[]
        for lo,hi in sorted(parts):
            if merged and lo<=merged[-1][1]: merged[-1]=(merged[-1][0],max(hi,merged[-1][1]))
            else: merged.append((lo,hi))
        joined[key]={'minutes':sum((b-a).total_seconds()/60 for a,b in merged),'latest':max(b for a,b in merged)}
    completions_by_learner={lid:{} for lid in lm}; joins_by_learner={lid:{} for lid in lm}; joins_by_session={sid:[] for sid in sm}
    for (lid,mid),t in completed.items(): completions_by_learner[lid][mid]=t
    for (lid,sid),v in joined.items(): joins_by_learner[lid][sid]=v; joins_by_session[sid].append(v)
    active=[l for l in learners if l['status']=='active']; released=[m for m in modules if dt(m['releasedAt'])<=now]; finished=[s for s in sessions if se(s)<=now]
    module_view=[]
    for m in modules:
        module_view.append({'id':m['id'],'order':m['order'],'title':text(m['title']),'release':stamp(dt(m['releasedAt'])),'currentWeek':dt(m['releasedAt'])<=now and (dt(m['releasedAt'])-start).days//7==(now-start).days//7,'upcoming':dt(m['releasedAt'])>now,'count':sum((l['id'],m['id']) in completed for l in active),'eligible':len(active)})
    session_view=[]
    for s in sessions:
        attending=joins_by_session[s['id']]
        session_view.append({'id':s['id'],'week':s['week'],'title':text(s['title']),'date':s['scheduledAt'],'state':'Finished' if se(s)<=now else 'Upcoming' if dt(s['scheduledAt'])>now else 'In progress','count':len(attending),'eligible':sum(eligible(l,dt(s['scheduledAt'])) for l in learners),'averageMinutes':round(sum(v['minutes'] for v in attending)/len(attending),1) if attending else None,'measuredAttendees':len(attending)})
    people=[]
    for l in learners:
        lid=l['id']; learner_completions=completions_by_learner[lid]; learner_joins=joins_by_learner[lid]; eligmods=[m for m in released if eligible(l,dt(m['releasedAt']))]; eligsess=[s for s in finished if eligible(l,dt(s['scheduledAt']))]
        history=[]
        for s in sessions:
            j=joined.get((lid,s['id'])); state='Not eligible' if not eligible(l,dt(s['scheduledAt'])) else 'Upcoming' if dt(s['scheduledAt'])>now else 'Joined' if j else 'In progress' if se(s)>now else 'No attendance recorded'
            history.append({'title':text(s['title']),'date':s['scheduledAt'],'state':state,'minutes':round(j['minutes'],1) if j else None})
        weeks=[]
        for i in range(p['weeks']):
            a=start+timedelta(days=7*i); b=a+timedelta(days=7)
            full=b<=now and dt(l['enrolledAt'])<=a and (l['status']=='active' or dt(l['withdrawnAt'])>=b)
            weeks.append({'week':i+1,'completedEligible':full,'modules':sum(a<=t<b for t in learner_completions.values()),'sessions':sum((lid,s['id']) in joined and a<=dt(s['scheduledAt'])<b for s in sessions)})
        denom=sum(w['completedEligible'] for w in weeks)
        latest=list(learner_completions.values())+[v['latest'] for v in learner_joins.values()]
        people.append({'id':lid,'name':text(l['name']),'title':text(l['title']),'status':l['status'],'withdrawnAt':stamp(dt(l['withdrawnAt'])) if l['status']=='withdrawn' else None,'completed':sum((lid,m['id']) in completed for m in eligmods),'moduleEligible':len(eligmods),'joined':sum((lid,s['id']) in joined for s in eligsess),'sessionEligible':len(eligsess),'latest':stamp(max(latest)) if latest else None,'modules':[{'title':text(m['title']),'release':m['releasedAt'],'completedAt':stamp(completed[(lid,m['id'])]) if (lid,m['id']) in completed else None,'state':'Upcoming' if dt(m['releasedAt'])>now else 'Not eligible' if not eligible(l,dt(m['releasedAt'])) else 'Released'} for m in modules],'sessions':history,'weekly':weeks,'completedWeeks':denom,'averageModules':round(sum(w['modules'] for w in weeks if w['completedEligible'])/denom,2) if denom else None,'averageSessions':round(sum(w['sessions'] for w in weeks if w['completedEligible'])/denom,2) if denom else None})
    numerator=sum((l['id'],m['id']) in completed for l in active for m in released); denominator=len(active)*len(released)
    return {'company':text(raw['company']['name']),'sponsor':{'name':text(raw['company']['sponsor']['name']),'title':text(raw['company']['sponsor']['title'])},'program':text(p['name']),'week':max(1,min(p['weeks'],(now-start).days//7+1)),'weeks':p['weeks'],'snapshot':stamp(now),'mock':raw.get('dataKind')=='fictional-challenge-data','active':len(active),'enrolled':len(learners),'withdrawn':len(learners)-len(active),'completed':numerator,'opportunities':denominator,'percent':math.floor(numerator/denominator*100+0.5) if denominator else None,'modules':module_view,'sessions':session_view,'people':people,'duplicateCompletions':duplicate}
class DataHandler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_GET(self):
        path=self.path.split('?')[0]
        if path=='/api/dashboard':
            # Fixed server-owned demo identity: never taken from a query or browser filter.
            try:
                raw=load_source(getattr(self.server,'source','fixture'))
                if raw['company']['id']!=self.server.access.company or raw['program']['id']!=self.server.access.program:
                    self.reply(403,{'error':'This dataset is outside the configured demo sponsor scope.'}); return
                self.reply(200,build(raw))
            except SourceError: self.reply(503,{'error':'The challenge API is unavailable. Retry shortly; no fixture or stale data was substituted.'})
            except (ValueError,KeyError,TypeError,OSError,OverflowError,AttributeError): self.reply(422,{'error':'Data could not be loaded or validated. Check the source file and README; no replacement values were used.'})
        elif path=='/':
            self.send_response(200); self.send_header('Content-Type','text/html; charset=utf-8'); self.send_header('Cache-Control','no-store'); self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'"); self.end_headers(); self.wfile.write((ROOT/'app'/'index.html').read_bytes())
        else: self.reply(404,{'error':'Not found'})
    def reply(self,status,value):
        self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(json.dumps(value,ensure_ascii=False,allow_nan=False).encode())

class Handler(DataHandler):
    def do_GET(self):
        path=self.path.split('?')[0]
        if path=='/login':
            self.send_html(login_page()); return
        if path in ('/','/api/dashboard') and not self.server.access.authorized(session_token(self.headers)):
            if path=='/':
                self.send_response(303);self.send_header('Location','/login');self.send_header('Cache-Control','no-store');self.end_headers()
            else:self.reply(401,{'error':'Sign in as the company sponsor to view this dashboard.'})
            return
        super().do_GET()
    def send_html(self,html,status=200):
        self.send_response(status);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Security-Policy',"default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'");self.end_headers();self.wfile.write(html.encode())
    def do_POST(self):
        path=self.path.split('?')[0]
        if path not in ('/login','/logout'):self.reply(404,{'error':'Not found'});return
        # Forms cannot be posted cross-site, including to this loopback app.
        origin=self.headers.get('Origin')
        if not origin or urlsplit(origin).netloc!=self.headers.get('Host') or urlsplit(origin).scheme not in ('http','https'):
            self.reply(403,{'error':'Request origin is not permitted.'});return
        if path=='/logout':
            self.server.access.logout(session_token(self.headers));self.send_response(303);self.send_header('Location','/login');self.send_header('Set-Cookie',self.server.access.cookie('',expired=True));self.send_header('Cache-Control','no-store');self.end_headers();return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=4096:raise ValueError()
            if self.headers.get('Content-Type','').split(';')[0]!='application/x-www-form-urlencoded':raise ValueError()
            values=parse_qs(self.rfile.read(length).decode('utf-8'),max_num_fields=3)
            result=self.server.access.login(values.get('username',[''])[0],values.get('password',[''])[0],self.client_address[0])
        except (ValueError,UnicodeError):self.reply(400,{'error':'Invalid sign-in request.'});return
        if result=='limited':self.send_html(login_page('Too many attempts. Please wait one minute.'),429);return
        if not result:self.send_html(login_page('Unable to sign in with those credentials.'),401);return
        self.send_response(303);self.send_header('Location','/');self.send_header('Set-Cookie',self.server.access.cookie(result));self.send_header('Cache-Control','no-store');self.end_headers()
if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Growth Institute sponsor dashboard')
    parser.add_argument('--source',choices=['live','fixture'],default='live')
    parser.add_argument('--port',type=int,default=8765)
    args=parser.parse_args()
    try: access=Access(load_config())
    except (ValueError,OSError,KeyError):raise SystemExit('Run python -B app/manage.py setup first. See README.md.')
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler);server.access=access;server.source=args.source
    print(f'Sponsor sign-in: http://127.0.0.1:{args.port}/ (source: {args.source})',flush=True)
    server.serve_forever()
