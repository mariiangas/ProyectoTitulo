# Deck base STKO `01_Wallace_1000`

Auditoría completa en `scripts/audit_stko_output.txt`. Este documento registra las definiciones del modelo de referencia de STKO a partir del cual se recuperaron los parámetros del preajuste de hormigón `ASDConcrete3D` (9P) empleados en el modelo sólido `rw2_solid_ladruno_embedment.ipynb`.

| ítem | líneas del deck (citadas) | referencia para el modelo sólido |
|---|---|---|
| nodos | 53 nodos, x -840 .. 1090, z 180 .. 4530 (muro x -485 .. 735, z 870 .. 4530 = 1220 x 3660; pedestal 1930 x 690) | origen del muro en (0, 0); base de 500 / 500 mm equivalente |
| hormigón | `nDMaterial ASDConcrete3D 1 29279.0 0.2 -Te ... -Ts ... -Td ... -Ce ... -Cs ... -Cd ... -implex -implexAlpha 1.0 -autoRegularization 7.924190762643707` | parámetros 9P recuperados mediante `scripts/recover_9p.py` |
| acero | `uniaxialMaterial Hysteretic 2 380.0 0.002 390.0 0.02 550.0 0.1 -380.0 -0.002 -390.0 -0.02 -550.0 -0.1 0.6 0.8 0.0 0.0` | parámetros de calibración de referencia |
| envolventes | `nDMaterial PlateFromPlaneStress 3 1 12500.0`, `nDMaterial PlateRebar 4 2 0.0`, `nDMaterial PlateRebar 11 2 90.0` | referencia de propiedades elásticas |
| sección base | `section ElasticMembranePlateSection 14 28198.0 0.2 500.0 0.0 1.0` | rigidez base escalada a `base_e` para espesor de 102 mm |
| apoyos | `fix 3 1 1 1 1 1 1`, ... 7 nodos en la base del pedestal (z 180) y cara superior expuesta (z 870) | `Fixed`: base del bloque, caras laterales y cara superior expuesta fijas |
| carga axial | `load 17 0.0 0.0 -124274.1 ...`, nodos 17, 18, 8 (3 nodos superiores centrales) | 372.8 kN distribuidos como tracción uniforme sobre la cara superior |
| peso propio | `# Loads.Force FaceForce`, e.g. `load 1 0.0 0.0 -109.83055734 ...`; total fz del deck = -383519.8 N (372822.3 axial + 10697.5 peso propio) | tracción superficial `-gamma_c * 102` en el muro |
| desplazamiento lateral | `sp` ux en 7 nodos superiores (z 4530), patrón 7 en serie 2 | desplazamiento cíclico impuesto en nodos superiores de control |
| serie temporal | `timeSeries Path 2 -dt 0.0303 -values {0.0 3.66 -3.66 ... 80.52 -80.52 0.0}` | historial de desplazamientos con los puntos de inversión del ensayo |
| etapas | 10 (gravedad) + 5000 (cíclico) incrementos | 10 incrementos de gravedad + etapa cíclica |
| algoritmos / sistema | `KrylovNewton -maxDim 10`, `Mumps -ICNTL14 200`, restricciones `Auto -autoPenalty 3` | `KrylovNewton(10)`, `Mumps(200)`, `Transformation` |
| monitor | corte basal = -1 x suma de reacciones de apoyo (Y), desplazamiento del nodo 4 (X) | suma de reacciones en x de los nodos con desplazamiento impuesto |

Los parámetros del hormigón para el modelo `rw2_solid_ladruno_embedment.ipynb` adaptan los valores de resistencia medidos en el ensayo (PEER 2006/07) manteniendo la formulación 9P de STKO (ver [materials.md](materials.md)).
