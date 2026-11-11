import re
import sys
import numpy as np
from apeGmsh.opensees.material.nd import ASDConcrete3D

text = open(sys.argv[1]).read()
blocks = re.findall(r"nDMaterial ASDConcrete3D (\d+) (\S+) (\S+)(.*?)-autoRegularization (\S+)", text, re.S)


def arr(block, flag):
    m = re.search(flag + r"((?:\s+[-\d.e+]+)+)", block)
    return np.array([float(v) for v in m.group(1).split()])


for tag, E, v, body, lch in blocks:
    E, v, lch = float(E), float(v), float(lch)
    Te, Ts, Td = arr(body, '-Te'), arr(body, '-Ts'), arr(body, '-Td')
    Ce, Cs, Cd = arr(body, '-Ce'), arr(body, '-Cs'), arr(body, '-Cd')
    ft, fc0, fcp, fcr, ecp = Ts[2], Cs[1], Cs.max(), Cs[-1], Ce[10]
    # tension: e2 = Gt/lch/ft + 0.2 ft/E + ep, ep = 0.5 ft/E
    Gt = (Te[3] - 0.2 * ft / E - 0.5 * ft / E) * ft * lch
    # compression: ecr = ecp + 2 (gc - Gc1)/(fcp + fcr)
    ec1 = fcp / E
    ec_pl = (ecp - ec1) * 0.4 + ec1
    Gc1 = fcp * (ecp - ec_pl) / 2.0
    Gc = (Gc1 + (Ce[11] - ecp) * (fcp + fcr) / 2.0) * lch
    # pscale from damage: pl = x - s / (E (1 - d))
    ep = 0.5 * ft / E
    ps_t = (Te[2] - Ts[2] / (E * (1 - Td[2]))) / ep
    cpl = [0.0, 0.0]
    for i in range(2, 11):
        cpl.append(cpl[-1] + (Ce[i] - cpl[-1]) * 0.7)
    i = 6
    ps_c = (Ce[i] - Cs[i] / (E * (1 - Cd[i]))) / cpl[i]
    ps_t, ps_c = round(ps_t, 6), round(ps_c, 6)
    p = dict(E=E, v=v, ft=ft, fc0=fc0, fcp=fcp, fcr=fcr, ecp=ecp, Gt=round(Gt, 6), Gc=round(Gc, 6),
             pscale_t=ps_t, pscale_c=ps_c)
    m = ASDConcrete3D.from_stko(**p, implex=True)
    err = max(np.abs(np.array(getattr(m, k)) - a).max() for k, a in
              (('Te', Te), ('Ts', Ts), ('Td', Td), ('Ce', Ce), ('Cs', Cs), ('Cd', Cd)))
    print(f'material {tag}: {p}')
    print(f'   lch deck {lch} | from_stko {m.lch_ref} | max curve diff {err:.3e}')
