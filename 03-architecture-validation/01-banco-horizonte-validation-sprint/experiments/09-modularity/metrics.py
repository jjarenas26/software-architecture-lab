import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'lab/services/payment-service/app'
mods={p.stem:p for p in ROOT.glob('*.py') if p.stem!='__init__'}
edges=set()
for name,path in mods.items():
    tree=ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node,ast.ImportFrom) and node.module and node.module.startswith('app.'):
            target=node.module.split('.')[1]
            if target in mods and target!=name: edges.add((name,target))
print('module,Ca,Ce,Instability')
for m in sorted(mods):
    ce=sum(1 for a,b in edges if a==m); ca=sum(1 for a,b in edges if b==m); denom=ca+ce; instability=ce/denom if denom else 0.0
    print(f'{m},{ca},{ce},{instability:.2f}')
print()
print('Interpretation: structural evidence only; not a universal architecture quality score.')
