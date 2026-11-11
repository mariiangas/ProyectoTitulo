# SW1-1 — modelos y parámetros

Espécimen **SW1-1**: muro rectangular esbelto con elementos de borde confinados, Zhang (Tongji, 2007); datos de Lu et al. (2015) y notas de THUShell. Unidades: N, mm, MPa. Este archivo describe únicamente la definición del modelo sólido (sin resultados). Los valores se leen desde las celdas de entrada y protocolo del cuaderno y de su deck emitido (`sw1_1_lu_solid_ladruno_embedment/sw1_1_lu_solid_ladruno_embedment.tcl`).

## Contenido

| archivo | modelo | guía |
|---|---|---|
| `sw1_1_lu_solid_ladruno_embedment.ipynb` | sólido: `LadrunoBrick` + barras embebidas `CorotTruss`, datos del espécimen | `sw1_1_lu_solid_ladruno_embedment.md` |

## Modelo sólido — `sw1_1_lu_solid_ladruno_embedment.ipynb`

### Parámetros

**Geometría**

| variable | valor | significado |
|---|---|---|
| `base_depth` | 550 | profundidad del bloque de fundación |
| `base_overhang` | 300 | sobreancho del bloque de fundación más allá de cada extremo del muro |
| `hw` | 2000 | altura del muro, desde la base hasta la carga lateral |
| `lbe` | 200 | ancho del elemento de borde / franja extrema |
| `lw` | 1000 | longitud del muro |
| `tw` | 125 | espesor del muro |

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
| `anchor_depth` | 500 | longitud de anclaje de barras verticales en la base |
| `be_cols` | 3 | columnas de barras de borde por elemento |
| `db10` | 10 | diámetro de barra phi10 |
| `db6` | 6 | diámetro de barra phi6 |
| `edge` | 23 | distancia del centro de la barra a la cara y al extremo del muro |
| `h_step` | 125 | espaciamiento de barras horizontales |
| `hoop_step` | 80 | espaciamiento de estribos / trabas |
| `k_perfect` | 1e+08 | penalización axial de adherencia perfecta (LadrunoEmbeddedRebar) |
| `web_n` | 5 | barras verticales del alma por cara |
| `web_step` | 125 | espaciamiento de barras del alma |

**Hormigón**

| variable | valor | significado |
|---|---|---|
| `ec` | 21400 | módulo de elasticidad E |
| `ecp` | 0.002 | deformación unitaria en el pico e_cp |
| `ecp_core` | 0.005 | e_cp del núcleo confinado |
| `fc0` | 5 | fin de la rama lineal f_c0 |
| `fc0_core` | 10 | f_c0 del núcleo confinado |
| `fcp` | 20.7 | resistencia máxima a compresión f_cp |
| `fcp_core` | 25 | f_cp del núcleo confinado |
| `fcr` | 4.14 | resistencia residual f_cr |
| `fcr_core` | 20 | f_cr del núcleo confinado |
| `ft` | 2.07 | resistencia a la tracción f_t |
| `gc` | 30 | energía de fractura en compresión G_c |
| `gc_core` | 60 | G_c del núcleo confinado |
| `gt` | 0.12595 | energía de fractura en tracción G_t |
| `nu` | 0.2 | coeficiente de Poisson |
| `pscale_c` | 0.3 | escala de deformación plástica en compresión |
| `pscale_t` | 0.3 | escala de deformación plástica en tracción |

**Acero**

| variable | valor | significado |
|---|---|---|
| `b_h` | 0.01 | razón de endurecimiento utilizada para la tensión al 2 % |
| `es10` | 202700 | módulo de elasticidad phi10 |
| `es6` | 200600 | módulo de elasticidad phi6 |
| `eu` | 0.12 | deformación unitaria en f_u |
| `fu10` | 554 | tensión última de phi10 |
| `fu6` | 479 | tensión última de phi6 |
| `fy10` | 379 | tensión de fluencia de phi10 |
| `fy6` | 392 | tensión de fluencia de phi6 |
| `k2` | 0.914634 | tensión al 2 % = f_y + k2 (f_u - f_y) |
| `pinch_x` | 0.5 | estrangulamiento (pinching) Hysteretic, deformación |
| `pinch_y` | 0.8 | estrangulamiento (pinching) Hysteretic, fuerza |
| `s2_10` | 539.061 | tensión de phi10 al 2 % |
| `s2_6` | 471.573 | tensión de phi6 al 2 % |

**Partes elásticas**

| variable | valor | significado |
|---|---|---|
| `base_e` | 71760 | módulo elástico del bloque de fundación (sólido: escalado por ancho fuera del plano / t_w) |

**Cargas**

| variable | valor | significado |
|---|---|---|
| `gamma_c` | 2.3544e-05 | peso unitario del hormigón (peso propio) |
| `p_axial` | 246000 | carga axial |

**Protocolo**

| variable | valor | significado |
|---|---|---|
| `peaks` | 24 puntos de inversión, -21.3 a 20.2 mm | desplazamiento superior impuesto (registro del ensayo) |
| `d_step` | 0.25 | incremento de desplazamiento |
| `n_cyclic` | 2378 | incrementos cíclicos |

### Modelo y solución

| ítem | valor |
|---|---|
| modelo | `BasicBuilder -ndm 3 -ndf 3` |
| elementos | `CorotTruss`, `LadrunoBrick`, `LadrunoEmbeddedRebar` (4729 elementos, 2552 nodos) |
| secciones | - |
| materiales nD | `ASDConcrete3D`, `ElasticIsotropic` |
| materiales uniaxiales | `Hysteretic` |
| transformación geométrica | - |
| integración de viga | - |
| procesos | 2 rangos MPI (`OpenSeesMP`) |
| constraints / numberer / system | `Transformation` / `ParallelRCM` / `Mumps -ICNTL14 200 -matrixType 0` |
| algoritmo | `KrylovNewton -maxDim 10` |
| escala de alternativas (cíclico) | `KrylovNewton -maxDim 10`, `ModifiedNewton -initial`, `KrylovNewton`, `NewtonLineSearch -type Bisection` |
| etapa de gravedad | `LoadControl 0.1` x 10, `test NormDispIncr 0.0001 50 0 2` |
| etapa cíclica | `LoadControl 0.00042052144659377626` x 2378, `test NormDispIncr 0.0001 100 0 2` |
| registrador | `ladruno -N displacement reactionForce -R 2` |
