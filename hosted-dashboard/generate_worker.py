from pathlib import Path
import json,sys
r=Path.cwd();root=r.parent
sys.path.insert(0,str(root/'app'))
from access import login_page
from server import build
html=(root/'app/index.html').read_text(encoding='utf-8-sig')
login=login_page().replace('This local challenge demo uses a provisioned sponsor account. Learners do not have sponsor access.','Use the reviewer credentials supplied with this application.').replace('<p role="status"></p>','<p role="status"><!--error--></p>')
source='const DASHBOARD_HTML='+json.dumps(html,ensure_ascii=False)+';\nconst LOGIN_HTML='+json.dumps(login,ensure_ascii=False)+';\n'+(r/'worker/logic.js').read_text(encoding='utf-8-sig')
(r/'worker/index.js').write_text(source,encoding='utf-8')
(r/'tests').mkdir(exist_ok=True)
raw=json.loads((root/'Growth_Institute_Dashboard_Data.json').read_text(encoding='utf-8-sig'))
(r/'tests/fixture.json').write_text(json.dumps(raw,ensure_ascii=False),encoding='utf-8')
(r/'tests/expected.json').write_text(json.dumps(build(raw),ensure_ascii=False),encoding='utf-8')
