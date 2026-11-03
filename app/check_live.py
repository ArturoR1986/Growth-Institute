from source import load_source
from server import build
v=build(load_source('live'))
print('Live /all integration passed')
print('Snapshot:',v['snapshot'])
print('Enrolled / active / withdrawn:',v['enrolled'],v['active'],v['withdrawn'])
print('Completion:',v['completed'],'/',v['opportunities'])
print('Source raw records are memory-only; no raw export was saved.')
