// Hosting runtime: same sponsor-safe model as app/server.py, verified by parity tests.
const DAY=86400000, WEEK=7*DAY;
const date=v=>{if(typeof v!=='string'||!v.endsWith('Z')||!Number.isFinite(Date.parse(v)))throw Error('Invalid UTC timestamp');return Date.parse(v)};
const iso=v=>new Date(v).toISOString();
const text=v=>{if(typeof v!=='string'||v.length>500)throw Error('Invalid text');return v};
const round=(v,n=2)=>Math.round((v+Number.EPSILON)*10**n)/10**n;
export function build(raw){
 if(raw.schemaVersion!=='1.0')throw Error('Unsupported schema');
 const now=date(raw.generatedAt),p=raw.program,start=date(p.startsAt),end=date(p.endsAt);
 if(!Number.isInteger(p.weeks)||p.weeks<1||p.weeks>104||end<=start)throw Error('Invalid program');
 const records=k=>{if(!Array.isArray(raw[k])||raw[k].length>20000)throw Error('Invalid record list');const ids=new Set;for(const row of raw[k]){if(!row||typeof row.id!=='string'||!row.id||row.id.length>100||ids.has(row.id))throw Error('Invalid ID');ids.add(row.id)}return raw[k]};
 const learners=records('learners'),modules=[...records('modules')].sort((a,b)=>a.order-b.order),sessions=[...records('sessions')].sort((a,b)=>date(a.scheduledAt)-date(b.scheduledAt));
 const lm=new Map(learners.map(l=>[l.id,l])),mm=new Map(modules.map(m=>[m.id,m])),sm=new Map(sessions.map(s=>[s.id,s]));
 for(const l of learners){text(l.name);text(l.title);if(date(l.enrolledAt)>start||!['active','withdrawn'].includes(l.status))throw Error('Invalid enrollment');if(l.status==='active'&&'withdrawnAt'in l)throw Error('Contradictory withdrawal');if(l.status==='withdrawn'&&(date(l.withdrawnAt)<date(l.enrolledAt)||date(l.withdrawnAt)>now))throw Error('Invalid withdrawal')}
 const orders=new Set;for(const m of modules){text(m.title);date(m.releasedAt);if(!Number.isInteger(m.order)||m.order<1||orders.has(m.order))throw Error('Invalid module order');orders.add(m.order)}
 for(const s of sessions){text(s.title);if(!Number.isInteger(s.week)||s.week!==Math.floor((date(s.scheduledAt)-start)/WEEK)+1||s.week<1||s.week>p.weeks||!mm.has(s.moduleId)||typeof s.durationMinutes!=='number'||!Number.isFinite(s.durationMinutes)||s.durationMinutes<=0||s.durationMinutes>=1440)throw Error('Invalid session')}
 const eligible=(l,t)=>date(l.enrolledAt)<=t&&(l.status==='active'||t<date(l.withdrawnAt)),se=s=>date(s.scheduledAt)+s.durationMinutes*60000;
 const completed=new Map(learners.map(l=>[l.id,new Map])),joined=new Map(learners.map(l=>[l.id,new Map]));let duplicate=0;
 if(!Array.isArray(raw.completions)||!Array.isArray(raw.attendance)||raw.completions.length>100000||raw.attendance.length>100000)throw Error('Invalid events');
 for(const c of raw.completions){const l=lm.get(c.learnerId),m=mm.get(c.moduleId),t=date(c.completedAt);if(!l||!m||t<date(m.releasedAt)||!eligible(l,t)||t>now)throw Error('Contradictory completion');const map=completed.get(l.id);if(map.has(m.id))duplicate++;map.set(m.id,Math.min(t,map.get(m.id)??t))}
 const intervals=new Map;
 for(const a of raw.attendance){const l=lm.get(a.learnerId),s=sm.get(a.sessionId),begin=date(a.joinedAt),finish=date(a.leftAt);if(!l||!s||finish<=begin||!eligible(l,date(s.scheduledAt))||begin>now)throw Error('Invalid attendance');const lo=Math.max(begin,date(s.scheduledAt),date(l.enrolledAt)),hi=Math.min(finish,se(s),now,l.status==='withdrawn'?date(l.withdrawnAt):Infinity);if(hi<=lo)throw Error('No positive overlap');const key=JSON.stringify([l.id,s.id]);if(!intervals.has(key))intervals.set(key,[]);intervals.get(key).push([lo,hi])}
 const bySession=new Map(sessions.map(s=>[s.id,[]]));
 for(const [key,parts]of intervals){parts.sort((a,b)=>a[0]-b[0]);const merged=[];for(const [lo,hi]of parts){const last=merged.at(-1);if(last&&lo<=last[1])last[1]=Math.max(hi,last[1]);else merged.push([lo,hi])}const value={minutes:merged.reduce((n,[a,b])=>n+(b-a)/60000,0),latest:Math.max(...merged.map(x=>x[1]))};const [lid,sid]=JSON.parse(key);joined.get(lid).set(sid,value);bySession.get(sid).push(value)}
 const active=learners.filter(l=>l.status==='active'),released=modules.filter(m=>date(m.releasedAt)<=now),finished=sessions.filter(s=>se(s)<=now);
 const mv=modules.map(m=>({id:m.id,order:m.order,title:text(m.title),release:iso(date(m.releasedAt)),currentWeek:date(m.releasedAt)<=now&&Math.floor((date(m.releasedAt)-start)/WEEK)===Math.floor((now-start)/WEEK),upcoming:date(m.releasedAt)>now,count:active.filter(l=>completed.get(l.id).has(m.id)).length,eligible:active.length}));
 const sv=sessions.map(s=>{const attending=bySession.get(s.id);return {id:s.id,week:s.week,title:text(s.title),date:s.scheduledAt,state:se(s)<=now?'Finished':date(s.scheduledAt)>now?'Upcoming':'In progress',count:attending.length,eligible:learners.filter(l=>eligible(l,date(s.scheduledAt))).length,averageMinutes:attending.length?round(attending.reduce((n,v)=>n+v.minutes,0)/attending.length,1):null,measuredAttendees:attending.length}});
 const people=learners.map(l=>{const cm=completed.get(l.id),jm=joined.get(l.id),em=released.filter(m=>eligible(l,date(m.releasedAt))),es=finished.filter(s=>eligible(l,date(s.scheduledAt)));
 const history=sessions.map(s=>{const j=jm.get(s.id);return {title:text(s.title),date:s.scheduledAt,state:!eligible(l,date(s.scheduledAt))?'Not eligible':date(s.scheduledAt)>now?'Upcoming':j?'Joined':se(s)>now?'In progress':'No attendance recorded',minutes:j?round(j.minutes,1):null}});
 const weeks=Array.from({length:p.weeks},(_,i)=>{const a=start+WEEK*i,b=a+WEEK;return {week:i+1,completedEligible:b<=now&&date(l.enrolledAt)<=a&&(l.status==='active'||date(l.withdrawnAt)>=b),modules:[...cm.values()].filter(t=>a<=t&&t<b).length,sessions:sessions.filter(s=>jm.has(s.id)&&a<=date(s.scheduledAt)&&date(s.scheduledAt)<b).length}});
 const denom=weeks.filter(w=>w.completedEligible).length,latest=[...cm.values(),...[...jm.values()].map(v=>v.latest)];
 return {id:l.id,name:text(l.name),title:text(l.title),status:l.status,withdrawnAt:l.status==='withdrawn'?iso(date(l.withdrawnAt)):null,completed:em.filter(m=>cm.has(m.id)).length,moduleEligible:em.length,joined:es.filter(s=>jm.has(s.id)).length,sessionEligible:es.length,latest:latest.length?iso(Math.max(...latest)):null,modules:modules.map(m=>({title:text(m.title),release:m.releasedAt,completedAt:cm.has(m.id)?iso(cm.get(m.id)):null,state:date(m.releasedAt)>now?'Upcoming':!eligible(l,date(m.releasedAt))?'Not eligible':'Released'})),sessions:history,weekly:weeks,completedWeeks:denom,averageModules:denom?round(weeks.filter(w=>w.completedEligible).reduce((n,w)=>n+w.modules,0)/denom):null,averageSessions:denom?round(weeks.filter(w=>w.completedEligible).reduce((n,w)=>n+w.sessions,0)/denom):null}
 });
 const numerator=active.reduce((n,l)=>n+released.filter(m=>completed.get(l.id).has(m.id)).length,0),denominator=active.length*released.length;
 return {company:text(raw.company.name),sponsor:{name:text(raw.company.sponsor.name),title:text(raw.company.sponsor.title)},program:text(p.name),week:Math.max(1,Math.min(p.weeks,Math.floor((now-start)/WEEK)+1)),weeks:p.weeks,snapshot:iso(now),mock:raw.dataKind==='fictional-challenge-data',active:active.length,enrolled:learners.length,withdrawn:learners.length-active.length,completed:numerator,opportunities:denominator,percent:denominator?Math.round(numerator/denominator*100):null,modules:mv,sessions:sv,people,duplicateCompletions:duplicate};
}
const FIELDS={program:['id','name','weeks','startsAt','endsAt'],company:['id','name'],learners:['id','name','title','status','enrolledAt','withdrawnAt'],modules:['id','order','title','releasedAt'],completions:['learnerId','moduleId','completedAt'],sessions:['id','week','moduleId','title','scheduledAt','durationMinutes'],attendance:['sessionId','learnerId','joinedAt','leftAt']};
export function project(raw){const keep=(row,keys)=>Object.fromEntries(keys.filter(k=>k in row).map(k=>[k,row[k]]));const result={schemaVersion:'1.0',dataKind:'fictional-challenge-data',generatedAt:raw.generatedAt};for(const[k,keys]of Object.entries(FIELDS))result[k]=['program','company'].includes(k)?keep(raw[k],keys):raw[k].map(row=>keep(row,keys));result.company.sponsor=keep(raw.company.sponsor,['name','title']);return result}
let cached=null,cacheUntil=0;
async function source(){if(cached&&Date.now()<cacheUntil)return cached;let response;try{response=await fetch('https://jobs.growthinstitute.com/api/challenge/all',{headers:{Accept:'application/json','User-Agent':'GrowthInstituteSponsorChallenge/1.0'},signal:AbortSignal.timeout(15000),redirect:'manual'});if(!response.ok){console.error('Challenge API status:',response.status);throw Error('Upstream status '+response.status)}const body=await response.text();if(body.length>2000000)throw Error();const safe=project(JSON.parse(body));cached=safe;cacheUntil=Date.now()+60000;return safe}catch(error){console.error('Challenge source failed:',error.name,String(error.message).slice(0,160));throw new SourceError()}}
class SourceError extends Error{}
const encoder=new TextEncoder,hex=bytes=>[...new Uint8Array(bytes)].map(x=>x.toString(16).padStart(2,'0')).join('');
const equal=(a,b)=>{let diff=a.length^b.length;for(let i=0;i<Math.max(a.length,b.length);i++)diff|=(a.charCodeAt(i)||0)^(b.charCodeAt(i)||0);return diff===0};
async function hashPassword(password,salt){if(!/^[a-f0-9]{32}$/.test(salt))throw Error('Invalid configuration');const bytes=Uint8Array.from(salt.match(/../g),x=>parseInt(x,16));const key=await crypto.subtle.importKey('raw',encoder.encode(password),'PBKDF2',false,['deriveBits']);return hex(await crypto.subtle.deriveBits({name:'PBKDF2',salt:bytes,iterations:100000,hash:'SHA-256'},key,256))}
const sign=async(data,secret)=>{const k=await crypto.subtle.importKey('raw',encoder.encode(secret),{name:'HMAC',hash:'SHA-256'},false,['sign']);return hex(await crypto.subtle.sign('HMAC',k,encoder.encode(data)))};
function tokenFrom(request){return (request.headers.get('Cookie')||'').split(';').map(x=>x.trim()).find(x=>x.startsWith('__Host-gi_session='))?.slice(18)||''}
const cookie=(value,age=3600)=>`__Host-gi_session=${value}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=${age}`;
function respond(body,status=200,headers={}){return new Response(body,{status,headers:{'Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'same-origin','Content-Security-Policy':"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; form-action 'self'; frame-ancestors 'none'",...headers}})}
const json=(value,status=200)=>respond(JSON.stringify(value),status,{'Content-Type':'application/json; charset=utf-8'});
const redirect=(path,c)=>respond('',303,{'Location':path,...(c?{'Set-Cookie':c}:{})});
async function keyFor(request,value){const u=new URL(request.url);return hex(await crypto.subtle.digest('SHA-256',encoder.encode(value)))}
async function session(request,env){const token=tokenFrom(request);if(!token||token.length>1000)return false;const parts=token.split('.');if(parts.length!==3)return false;const[nonce,expires,signature]=parts;if(!/^\d{13}$/.test(expires)||Number(expires)<=Date.now())return false;const data=nonce+'.'+expires+'.'+env.SPONSOR_COMPANY_ID+'.'+env.SPONSOR_PROGRAM_ID;if(!equal(signature,await sign(data,env.SESSION_SECRET)))return false;return !!await env.DB.prepare('SELECT token_hash FROM reviewer_sessions WHERE token_hash = ? AND expires_at > ?').bind(await keyFor(request,token),Date.now()).first()}

export async function handle(request,env){
 const u=new URL(request.url),path=u.pathname;
 if(!env.DB||!env.SESSION_SECRET||!env.REVIEWER_PASSWORD_HASH||!env.REVIEWER_PASSWORD_SALT||!env.REVIEWER_USERNAME||!env.SPONSOR_COMPANY_ID||!env.SPONSOR_PROGRAM_ID)return json({error:'Reviewer access is not configured.'},503);
 if(request.method==='GET'&&path==='/login')return respond(LOGIN_HTML,200,{'Content-Type':'text/html; charset=utf-8'});
 if(request.method==='POST'&&['/login','/logout'].includes(path)){
  if(request.headers.get('Origin')!==u.origin)return json({error:'Request origin is not permitted.'},403);
  if(path==='/logout'){const token=tokenFrom(request);if(token)await env.DB.prepare('DELETE FROM reviewer_sessions WHERE token_hash = ?').bind(await keyFor(request,token)).run();return redirect('/login',cookie('',0))}
  if(!(request.headers.get('Content-Type')||'').startsWith('application/x-www-form-urlencoded'))return json({error:'Invalid sign-in request.'},400);
  const ip=request.headers.get('CF-Connecting-IP')||'unknown',now=Date.now(),ipHash=await sign(ip,env.SESSION_SECRET);
  await env.DB.batch([env.DB.prepare('DELETE FROM reviewer_sessions WHERE expires_at <= ?').bind(now),env.DB.prepare('DELETE FROM reviewer_attempts WHERE resets_at <= ?').bind(now)]);
  const attempt=await env.DB.prepare('INSERT INTO reviewer_attempts (ip_hash, attempts, resets_at) VALUES (?, 1, ?) ON CONFLICT(ip_hash) DO UPDATE SET attempts = attempts + 1 RETURNING attempts').bind(ipHash,now+60000).first();
  if(attempt.attempts>5)return respond(LOGIN_HTML.replace('<!--error-->','Too many attempts. Please wait one minute.'),429,{'Content-Type':'text/html; charset=utf-8','Retry-After':'60'});
  const body=await request.text();if(body.length>4096)return json({error:'Invalid sign-in request.'},400);const fields=new URLSearchParams(body),username=fields.get('username')||'',password=fields.get('password')||'';
  const hashed=await hashPassword(password,env.REVIEWER_PASSWORD_SALT);if(!equal(hashed,env.REVIEWER_PASSWORD_HASH)||!equal(username,env.REVIEWER_USERNAME))return respond(LOGIN_HTML.replace('<!--error-->','Unable to sign in with those credentials.'),401,{'Content-Type':'text/html; charset=utf-8'});
  const nonce=hex(crypto.getRandomValues(new Uint8Array(24))),expires=String(Date.now()+3600000),token=nonce+'.'+expires+'.'+await sign(nonce+'.'+expires+'.'+env.SPONSOR_COMPANY_ID+'.'+env.SPONSOR_PROGRAM_ID,env.SESSION_SECRET);
  await env.DB.prepare('INSERT INTO reviewer_sessions (token_hash, expires_at) VALUES (?, ?)').bind(await keyFor(request,token),Number(expires)).run();return redirect('/',cookie(token))
 }
 if(request.method!=='GET')return json({error:'Not found'},404);
 if(!['/','/api/dashboard'].includes(path))return json({error:'Not found'},404);
 if(!await session(request,env))return path==='/'?redirect('/login'):json({error:'Sign in as the company sponsor to view this dashboard.'},401);
 if(path==='/')return respond(DASHBOARD_HTML,200,{'Content-Type':'text/html; charset=utf-8'});
 try{const raw=await source();if(raw.company.id!==env.SPONSOR_COMPANY_ID||raw.program.id!==env.SPONSOR_PROGRAM_ID)return json({error:'This dataset is outside the configured sponsor scope.'},403);return json(build(raw))}
 catch(error){return error instanceof SourceError?json({error:'The challenge API is unavailable. Retry shortly; no fixture or stale data was substituted.'},503):json({error:'Data could not be validated. No replacement values were used.'},422)}
}
export default {async fetch(request,env){try{return await handle(request,env)}catch(error){console.error('Hosted request failed:',error.name,String(error.message).slice(0,200));return json({error:'The dashboard is temporarily unavailable. Please retry.'},503)}}};



