# SW02 — modelos y parámetros

Espécimen **SW02**: muro de baja esbeltez (squat) a escala real, Pizarro Pohl, Kovarbasic & Stojadinovic (ETH Zurich); datos de JSE 2025, 151(4) 04025011, tesis doctoral, planos y ensayos de probetas. Unidades: N, mm, MPa. Este archivo describe únicamente la definición del modelo sólido (sin resultados). Los valores se leen desde las celdas de entrada y protocolo del cuaderno y de su deck emitido (`sw02_pizarro_solid_ladruno_embedment/sw02_pizarro_solid_ladruno_embedment.tcl`).

## Contenido

| archivo | modelo | guía |
|---|---|---|
| `sw02_pizarro_solid_ladruno_embedment.ipynb` | sólido: `LadrunoBrick` + barras embebidas `CorotTruss`, datos del espécimen | `sw02_pizarro_solid_ladruno_embedment.md` |

## Modelo sólido — `sw02_pizarro_solid_ladruno_embedment.ipynb`

### Parámetros

**Geometría**

| variable | valor | significado |
|---|---|---|
| `base_depth` | 500 | profundidad del bloque de fundación |
| `base_overhang` | 500 | sobreancho del bloque de fundación más allá de cada extremo del muro |
| `beam_h` | 500 | altura de la viga de carga |
| `beam_t` | 900 | ancho fuera del plano de la viga de carga |
| `hw` | 2550 | altura del muro, desde la base hasta la carga lateral |
| `lw` | 3000 | longitud del muro |
| `tw` | 200 | espesor del muro |

**Discretización**

| variable | valor | significado |
|---|---|---|
| `bar_refine` | 4 | segmento de barra = max_size / bar_refine |
| `brick` | ssp | formulación de LadrunoBrick |
| `max_size` | 200 | tamaño máximo de elemento |
| `record_all` | True | registrador en cada nodo de hormigón |

**Armadura**

| variable | valor | significado |
|---|---|---|
| `anchor` | 50 | distancia de retranqueo de barras verticales respecto al fondo de base / tope de viga |
| `db10` | 10 | diámetro de barra phi10 |
| `db16` | 16 | diámetro de barra phi16 |
| `edge10` | 35 | distancia del eje vertical de phi10 a la cara |
| `edge16` | 38 | distancia del eje de phi16 a la cara y al extremo del muro |
| `hoop_edge` | 25 | distancia del eje del estribo a la cara y al extremo del muro |
| `hoop_step` | 150 | espaciamiento de estribos / trabas |
| `k_perfect` | 1e+08 | penalización axial de adherencia perfecta (LadrunoEmbeddedRebar) |
| `v_step` | 150 | espaciamiento de barras verticales phi10 |

**Hormigón**

| variable | valor | significado |
|---|---|---|
| `ec` | 32145 | módulo de elasticidad E |
| `ecp` | 0.00197742 | deformación unitaria en el pico e_cp |
| `fc0` | 5 | fin de la rama lineal f_c0 |
| `fcp` | 28.5 | resistencia máxima a compresión f_cp |
| `fcr` | 1 | resistencia residual f_cr |
| `ft` | 2.7991 | resistencia a la tracción f_t |
| `gc` | 33 | energía de fractura en compresión G_c |
| `gt` | 0.133412 | energía de fractura en tracción G_t |
| `nu` | 0.2 | coeficiente de Poisson |
| `pscale_c` | 0.3 | escala de deformación plástica en compresión |
| `pscale_t` | 0.3 | escala de deformación plástica en tracción |

**Acero**

| variable | valor | significado |
|---|---|---|
| `es10` | 198970 | módulo de elasticidad phi10 |
| `es16` | 196490 | módulo de elasticidad phi16 |
| `eu10` | 0.0543 | deformación unitaria de phi10 en f_u |
| `eu16` | 0.0686 | deformación unitaria de phi16 en f_u |
| `fu10` | 596.19 | tensión última de phi10 |
| `fu16` | 612.33 | tensión última de phi16 |
| `fy10` | 523.65 | tensión de fluencia de phi10 |
| `fy16` | 523.52 | tensión de fluencia de phi16 |
| `pinch_x` | 0.5 | estrangulamiento (pinching) Hysteretic, deformación |
| `pinch_y` | 0.8 | estrangulamiento (pinching) Hysteretic, fuerza |
| `s2_10` | 569 | tensión de phi10 al 2 % |
| `s2_16` | 578 | tensión de phi16 al 2 % |

**Partes elásticas**

| variable | valor | significado |
|---|---|---|
| `base_e` | 272250 | módulo elástico del bloque de fundación (sólido: escalado por ancho fuera del plano / t_w) |
| `beam_e` | 148500 | módulo elástico de la viga de carga (sólido: escalado por ancho fuera del plano / t_w) |

**Cargas**

| variable | valor | significado |
|---|---|---|
| `gamma_c` | 2.3544e-05 | peso unitario del hormigón (peso propio) |
| `p_axial` | 1.8e+06 | carga axial |

**Protocolo**

| variable | valor | significado |
|---|---|---|
| `peaks` | 46 puntos de inversión, -25.98 a 25.32 mm | desplazamiento superior impuesto (registro del ensayo) |
| `d_step` | 0.25 | incremento de desplazamiento |
| `n_cyclic` | 3566 | incrementos cíclicos |

### Modelo y solución

| ítem | valor |
|---|---|
| modelo | `BasicBuilder -ndm 3 -ndf 3` |
| elementos | `CorotTruss`, `LadrunoBrick`, `LadrunoEmbeddedRebar` (10079 elementos, 5596 nodos) |
| secciones | - |
| materiales nD | `ASDConcrete3D`, `ElasticIsotropic` |
| materiales uniaxiales | `Hysteretic` |
| transformación geométrica | - |
| integración de viga | - |
| procesos | 2 rangos MPI (`OpenSeesMP`) |
| constraints / numberer / system | `Transformation` / `ParallelRCM` / `Mumps -ICNTL14 200 -matrixType 0` |
| algoritmo | `KrylovNewton -maxDim 10` |
| escala de alternativas (cíclico) | `KrylovNewton -maxDim 10`, `ModifiedNewton -initial`, `KrylovNewton`, `NewtonLineSearch -type Bisection` |
| etapa de gravedad | `LoadControl 0.1` x 10, `test EnergyIncr 0.0001 10 0 2` |
| etapa cíclica | `LoadControl 0.00028042624789680314` x 3566, `test NormDispIncr 0.0001 100 0 2` |
| registrador | `ladruno -N displacement reactionForce -R 2` |
