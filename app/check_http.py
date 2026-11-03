import json, threading, urllib.request, urllib.error
from http.server import HTTPServer
from server import Handler
from access import Access, password_hash
server=HTTPServer(('127.0.0.1',0),Handler)
server.access=Access({'username':'sponsor','salt':'ab'*16,'passwordHash':password_hash('test-password','ab'*16),'companyId':'cmp_northwind','programId':'prg_scaleup_os'})
cookie='gi_session='+server.access.issue()
def request(url):return urllib.request.urlopen(urllib.request.Request(url,headers={'Cookie':cookie}))
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
base='http://127.0.0.1:'+str(server.server_port)
try:
    with request(base+'/api/dashboard') as response:
        view=json.load(response)
        assert view['completed']==44 and view['opportunities']==66
        assert 'completions' not in view and 'attendance' not in view
        assert view['sessions'][5]['measuredAttendees']==5
    with request(base+'/') as response:
        html=response.read().decode('utf-8-sig')
        assert 'Team participation' in html and 'aria-expanded' in html
    for path in ['/Growth_Institute_Dashboard_Data.json','/app/server.py','/../README.md']:
        try: request(base+path);raise AssertionError('Unexpected public file')
        except urllib.error.HTTPError as error: assert error.code==404
    print('HTTP checks passed: safe API, template, and raw/source route denial.')
finally:
    server.shutdown();server.server_close();thread.join()
