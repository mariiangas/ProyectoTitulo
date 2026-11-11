import re
import sys
from collections import defaultdict
from pathlib import Path

d = Path(sys.argv[1])
nodes = {}
for l in (d / 'nodes.tcl').read_text().splitlines():
    m = re.match(r"\s*node (\d+) (\S+) (\S+) (\S+)", l)
    if m:
        nodes[int(m[1])] = tuple(float(v) for v in m.group(2, 3, 4))
xs = [c[0] for c in nodes.values()]; ys = [c[1] for c in nodes.values()]; zs = [c[2] for c in nodes.values()]
print(f'nodes {len(nodes)} | x {min(xs)} .. {max(xs)} | y {min(ys)} .. {max(ys)} | z {min(zs)} .. {max(zs)}')

groups = defaultdict(list)
flags = defaultdict(set)
for l in (d / 'elements.tcl').read_text().splitlines():
    s = l.strip()
    if not s.startswith('element '):
        continue
    p = s.split()
    etype = p[1]
    nn = {'ASDShellQ4': 4, 'ASDShellT3': 3, 'ShellMITC4': 4, 'ShellDKGQ': 4, 'ShellNLDKGQ': 4}.get(etype)
    if nn is None:
        groups[(etype, '?')].append([]); flags[(etype, '?')].add(' '.join(p[3:])[:60]); continue
    conn = [int(v) for v in p[3:3 + nn]]
    sec = p[3 + nn]
    groups[(etype, sec)].append(conn)
    flags[(etype, sec)].add(' '.join(p[4 + nn:]))
for (etype, sec), els in sorted(groups.items()):
    cs = [nodes[n] for e in els for n in e if n in nodes]
    if cs:
        print(f'{etype} sec {sec}: {len(els)} elems | x {min(c[0] for c in cs)} .. {max(c[0] for c in cs)} | '
              f'z {min(c[2] for c in cs)} .. {max(c[2] for c in cs)} | flags {flags[(etype, sec)]}')
    else:
        print(etype, sec, len(els), flags[(etype, sec)])

a = (d / 'analysis_steps.tcl').read_text()
fix = {}
for m in re.finditer(r"^\s*fix (\d+) ([\d ]+)$", a, re.M):
    fix[int(m[1])] = m[2].strip()
print(f'fix: {len(fix)} nodes, dof masks {set(fix.values())}')
fz = sorted({nodes[n][2] for n in fix}); print('  fixed z levels:', fz)
for z in fz:
    xx = sorted(nodes[n][0] for n in fix if nodes[n][2] == z)
    print(f'  z={z}: {len(xx)} nodes, x {xx[0]} .. {xx[-1]}')
sp = sorted({int(m[1]) for m in re.finditer(r"^\s*sp (\d+) (\d+) (\S+)", a, re.M)})
spd = {m[2] for m in re.finditer(r"^\s*sp (\d+) (\d+) (\S+)", a, re.M)}
print(f'sp: {len(sp)} nodes, dofs {spd}, z {sorted({nodes[n][2] for n in sp})}, x {sorted(nodes[n][0] for n in sp)[:3]}..{sorted(nodes[n][0] for n in sp)[-1:]}')
eq = re.findall(r"^\s*(equalDOF|rigidLink|rigidDiaphragm)\b.*$", a, re.M)
print('mp constraints:', len(eq), set(eq))
tot = [0.0, 0.0, 0.0]; big = []
for m in re.finditer(r"^\s*load (\d+) (\S+) (\S+) (\S+)", a, re.M):
    f = [float(m[2]), float(m[3]), float(m[4])]
    tot = [t + v for t, v in zip(tot, f)]
    if max(abs(v) for v in f) > 1000:
        big.append((int(m[1]), nodes.get(int(m[1])), f))
print(f'loads total fx {tot[0]:.1f} fy {tot[1]:.1f} fz {tot[2]:.1f} | big loads: {len(big)}')
for b in big[:12]:
    print('   ', b)
for m in re.finditer(r"^pattern Plain (\d+) (\d+)", a, re.M):
    print('pattern', m[1], 'series', m[2])
print('stage increments:', re.findall(r"set initial_num_incr (\d+)", a), '| total_duration', set(re.findall(r"set total_duration (\S+)", a)))
print('tests:', re.findall(r"^test (.*)$", a, re.M))
print('algorithms:', re.findall(r"^algorithm (.*)$", a, re.M))
print('constraints:', set(re.findall(r"^constraints (.*)$", a, re.M)), '| system', set(re.findall(r"^system (.*)$", a, re.M)))
print('mass lines:', len(re.findall(r"^\s*mass ", a, re.M)), '| exit present:', '\nexit' in a)
for m in re.finditer(r"set nodes_(X|Y)_\d+ \{([^}]*)\}", a):
    ids = [int(v) for v in m[2].split()]
    print(f'monitor {m[1]}: {ids[:8]} -> coords {[nodes[i] for i in ids[:3]]}')
for m in re.finditer(r"set monitor_value_(X|Y) \[expr (\S+) \* \$monitor_value_\w+ \+ (\S+)\]", a):
    print('monitor scale', m.groups())
