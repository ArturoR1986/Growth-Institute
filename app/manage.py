import argparse, json, secrets
from pathlib import Path
from getpass import getpass
from access import password_hash
ROOT=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser();parser.add_argument('command',choices=['setup']);args=parser.parse_args()
p=ROOT/'.local-config.json'
if p.exists():raise SystemExit('Account already configured. Keep it or explicitly remove .local-config.json to reprovision.')
username=input('Sponsor username [sponsor]: ').strip() or 'sponsor'
password=getpass('Choose a sponsor password (12+ characters): ')
if not 12<=len(password)<=200:raise SystemExit('Use 12–200 characters.')
if getpass('Confirm password: ')!=password:raise SystemExit('Passwords did not match.')
salt=secrets.token_hex(16)
p.write_text(json.dumps({'username':username,'salt':salt,'passwordHash':password_hash(password,salt),'companyId':'cmp_northwind','programId':'prg_scaleup_os'},indent=2))
print('Sponsor account configured locally. Credentials are not bundled in the repository.')
