# RW2 — modelos y parámetros

Espécimen **RW2**: muro rectangular con elementos de borde confinados, Thomsen & Wallace (1995); datos de Orakcal, Massone & Wallace (2006), PEER 2006/07. Unidades: N, mm, MPa. Este archivo describe únicamente la definición del modelo sólido (sin resultados). Los valores se leen desde las celdas de entrada y protocolo del cuaderno y de su deck emitido (`rw2_solid_ladruno_embedment/rw2_solid_ladruno_embedment.tcl`); las fuentes y supuestos de cada valor se encuentran en `context/`.

## Contenido

El notebook incluye los bloques **CREAR CORRIDA Y CONGELAR PARÁMETROS**,
**COMPARACIONES LOCALES** y **EXPORTAR Y ACTUALIZAR FICHA**. Cada análisis nuevo
se conserva en `runs/wallace_NNNN/`; consultar [historial](runs/indice.md) y
[guía de corridas](runs/README.md). Los datos experimentales globales y locales y sus
límites se documentan en [DatosExperimentales/README.md](DatosExperimentales/README.md).

| archivo | modelo | guía |
|---|---|---|
| `rw2_solid_ladruno_embedment.ipynb` | sólido: `LadrunoBrick` + barras embebidas `CorotTruss`, datos del espécimen | `rw2_solid_ladruno_embedment.md` |
| `DatosExperimentales/` | curva global y referencias locales del ensayo | `DatosExperimentales/README.md` |
| `context/` | fuentes, geometría y armadura, materiales, supuestos, calibración | `context/README.md` |

## Modelo sólido — `rw2_solid_ladruno_embedment.ipynb`

### Parámetros

**Geometría**

| variable | valor | significado |
|---|---|---|
| `base_depth` | 690 | profundidad del bloque de fundación |
| `base_overhang` | 355 | sobreancho del bloque de fundación más allá de cada extremo del muro |
| `h_conf` | 1220 | altura de la zona de borde confinada |
| `hw` | 3660 | altura del muro, desde la base hasta la carga lateral |
| `lbe` | 200 | ancho del elemento de borde / franja extrema |
| `lw` | 1220 | longitud del muro |
| `tw` | 102 | espesor del muro |

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
| `anchor_depth` | 640 | longitud de anclaje de barras verticales en la base |
| `be_step` | 51 | espaciamiento de barras de borde |
| `db2` | 6.35 | diámetro de barra #2 |
| `db3` | 9.53 | diámetro de barra #3 |
| `dbw` | 4.76 | diámetro del alambre para estribos |
| `edge` | 19 | distancia del centro de la barra a la cara y al extremo del muro |
| `hoop_step` | 76 | espaciamiento de estribos / trabas |
| `k_perfect` | 1e+08 | penalización axial de adherencia perfecta (LadrunoEmbeddedRebar) |
| `web_step` | 191 | espaciamiento de barras del alma |

**Hormigón**

| variable | valor | significado |
|---|---|---|
| `ec` | 31030 | módulo de elasticidad E |
| `ecp_conf` | 0.0033 | e_cp confinado |
| `ecp_unconf` | 0.0021 | e_cp no confinado |
| `fc0` | 10 | fin de la rama lineal f_c0 |
| `fcp_conf` | 47.6 | f_cp confinado |
| `fcp_unconf` | 42.8 | f_cp no confinado |
| `fcr` | 10 | resistencia residual f_cr |
| `ft` | 2.03 | resistencia a la tracción f_t |
| `gc` | 36 | energía de fractura en compresión G_c |
| `gt` | 0.143543 | energía de fractura en tracción G_t |
| `nu` | 0.2 | coeficiente de Poisson |
| `pscale_c` | 0.3 | escala de deformación plástica en compresión |
| `pscale_t` | 0.3 | escala de deformación plástica en tracción |

**Acero**

| variable | valor | significado |
|---|---|---|
| `b_h` | 0.02 | razón de endurecimiento utilizada para la tensión al 2 % |
| `es` | 200000 | módulo de elasticidad E_s |
| `eu2` | 0.08 | deformación unitaria de #2 en f_u |
| `eu3` | 0.1 | deformación unitaria de #3 en f_u |
| `fu2` | 586 | tensión última de #2 |
| `fu3` | 641 | tensión última de #3 |
| `fy2` | 448 | tensión de fluencia de #2 |
| `fy3` | 434 | tensión de fluencia de #3 |
| `pinch_x` | 0.6 | estrangulamiento (pinching) Hysteretic, deformación |
| `pinch_y` | 0.8 | estrangulamiento (pinching) Hysteretic, fuerza |
| `s2_2` | 519.04 | tensión de #2 al 2 % |
| `s2_3` | 505.32 | tensión de #3 al 2 % |

**Partes elásticas**

| variable | valor | significado |
|---|---|---|
| `base_e` | 138225 | módulo elástico del bloque de fundación (sólido: escalado por ancho fuera del plano / t_w) |

**Cargas**

| variable | valor | significado |
|---|---|---|
| `gamma_c` | 2.3544e-05 | peso unitario del hormigón (peso propio) |
| `p_axial` | 372822 | carga axial |

**Protocolo**

| variable | valor | significado |
|---|---|---|
| `peaks` | 40 puntos de inversión, -79.57 a 80.46 mm | desplazamiento superior impuesto (registro del ensayo) |
| `d_step` | 0.5 | incremento de desplazamiento |
| `n_cyclic` | 5209 | incrementos cíclicos |

### Modelo y solución

| ítem | valor |
|---|---|
| modelo | `BasicBuilder -ndm 3 -ndf 3` |
| elementos | `CorotTruss`, `LadrunoBrick`, `LadrunoEmbeddedRebar` (6966 elementos, 3862 nodos) |
| secciones | - |
| materiales nD | `ASDConcrete3D`, `ElasticIsotropic` |
| materiales uniaxiales | `Hysteretic` |
| transformación geométrica | - |
| integración de viga | - |
| procesos | 1 proceso (`OpenSeesMP`, Windows) |
| constraints / numberer / system | `Transformation` / `RCM` / `UmfPack` |
| algoritmo | `KrylovNewton -maxDim 10` |
| escala de alternativas (cíclico) | `KrylovNewton -maxDim 10`, `ModifiedNewton -initial`, `KrylovNewton`, `NewtonLineSearch -type Bisection` |
| etapa de gravedad | `LoadControl 0.1` x 10, `test NormDispIncr 0.0001 50 0 2` |
| etapa cíclica | `LoadControl 0.0001919754271453254` x 5209, `test NormDispIncr 0.0001 100 0 2` |
| registrador | `ladruno -N displacement reactionForce -R 2` |
