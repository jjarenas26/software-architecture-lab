import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'lab/services/payment-service/app'
forbidden={'clients','repository','main','service'}
violations=[]
path=ROOT/'domain.py'
tree=ast.parse(path.read_text())
for node in ast.walk(tree):
    if isinstance(node,ast.ImportFrom) and node.module and node.module.startswith('app.'):
        target=node.module.split('.')[1]
        if target in forbidden: violations.append((node.lineno,node.module))
    if isinstance(node,ast.Import):
        for alias in node.names:
            if alias.name.startswith('app.') and alias.name.split('.')[1] in forbidden:
                violations.append((node.lineno,alias.name))
if violations:
    print('FAIL - forbidden domain dependencies:',violations); raise SystemExit(2)
print('PASS - domain has no dependency on infrastructure or application entry points')
