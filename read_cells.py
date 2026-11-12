import json

with open('Notebooks/RW2_Wallace/rw2_solid_ladruno_embedment.ipynb', encoding='utf-8') as f:
    nb = json.load(f)

for i in [5, 7, 9]:
    c = nb['cells'][i]
    print(f"=== CELL {i} ===")
    print(''.join(c.get('source', [])))
