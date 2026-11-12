import json

with open('Notebooks/RW2_Wallace/rw2_solid_ladruno_embedment.ipynb', encoding='utf-8') as f:
    nb = json.load(f)

for i in range(0, 25):
    c = nb['cells'][i]
    print(f"=== CELL {i} ({c['cell_type']}) ===")
    src = ''.join(c.get('source', []))
    print(src[:500] + ('...' if len(src) > 500 else ''))
    print("-" * 50)
