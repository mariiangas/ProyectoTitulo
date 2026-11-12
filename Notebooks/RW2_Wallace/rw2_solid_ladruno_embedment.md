# rw2_solid_ladruno_embedment.ipynb — descripción del modelo

Espécimen **RW2**, Thomsen & Wallace (1995): muro rectangular (1220 x 3660 mm, t = 102 mm, elementos de borde de 200 mm, pedestal de 1930 x 690 mm, carga axial de 372.8 kN) construido con **hexaedros** (`LadrunoBrick`, formulación estabilizada de un punto `ssp`) y **barras discretas** embebidas en el hormigón (`LadrunoEmbeddedRebar`, adherencia perfecta, barras `CorotTruss`). Unidades: **N, mm, MPa**.

| ítem | en este modelo | fuente |
|---|---|---|
| muro | 1220 x 3660 x 102 mm, elementos de borde de 200 mm, dividido en z = 1220 mm (zona confinada) | PEER 607 sec. 7.1.1, Fig. 7.1-7.3 |
| pedestal | 1930 x 690 x 102 mm, un volumen, elástico, E x (500 / 102) para conservar la rigidez en el plano de la base de referencia | PEER 607 Fig. 7.2; E de referencia |
| hormigón | `ASDConcrete3D`, preajuste STKO `Concrete (9P)`, no confinado 42.8 MPa / confinado 47.6 MPa; los valores no reportados conservan la línea base calibrada de STKO | PEER 607 Tablas 7.1-7.2 |
| barras de borde | 8 #3 (db 9.53) por extremo, 3 @ 51 desde 19 mm, dos capas 19 / 64 / 19 | PEER 607 Fig. 7.3a |
| barras del alma | #2 (db 6.35) @ 191, dos mallas, vertical y horizontal | PEER 607 Fig. 7.3a |
| estribos | alambre de 4.76 mm @ 76 en los 1220 mm inferiores (`lw`) | PEER 607 sec. 7.1.1, Fig. 7.3a |
| acero | `Hysteretic` por tipo de barra: #3 434 / 505 al 2 % / 641 al 10 %; #2 y alambre 448 / 519 / 586 al 8 %; pinching 0.6 / 0.8 | Tabla 7.1, PEER 2024/11 Tabla A.1; pinching de referencia |
| protocolo | 40 puntos de inversión del registro de ensayo, incrementos de 0.5 mm | archivo de ensayo `DatosExperimentales/ExperimentalData.csv` |

Se ejecuta con el `OpenSeesMP` de Ladruno en **2 particiones** (apeGmsh asigna cada restricción al rango de su hexaedro anfitrión y declara como nodo fantasma el nodo de la barra cuando se requiere). Evidencia de cada valor: `context/`.

Carpeta de ejecución: `rw2_solid_ladruno_embedment/`. Fuentes, calibración y supuestos: `context/` (`calibration_solid.md`, `assumptions.md`).

## Armadura

Centros de barra (x desde el extremo izquierdo del muro, y desde el plano medio del muro):

- **borde**: 8 #3 por extremo, x = 19, 70, 121, 172 (y simétrico), y = +-32 (19 / 64 / 19).
- **alma vertical**: #2 en 3 @ 191 centradas en el muro, x = 323.5, 514.5, 705.5, 896.5, y = +-32.
- **alma horizontal**: #2 @ 191 a lo largo de la altura, x desde 19 hasta 1201, y = +-32 (mismo plano que las barras verticales, idealización reticulada).
- **estribos**: rectángulos cerrados de 4.76 mm rodeando cada grupo de 8 barras, @ 76 desde z = 38 hasta 1220.

Las barras verticales se extienden desde `anchor_depth` dentro de la base hasta 19 mm por debajo de la parte superior (los ganchos a 90 grados no se modelan). Todas las barras: `CorotTruss` en su propia malla lineal, unidas a los hexaedros mediante `LadrunoEmbeddedRebar` con adherencia perfecta.

## Parámetros

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

## Modelo y solución

| ítem | valor |
|---|---|
| modelo | `BasicBuilder -ndm 3 -ndf 3` |
| elementos | `CorotTruss`, `LadrunoBrick`, `LadrunoEmbeddedRebar` (6966 elementos, 3862 nodos) |
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
| etapa cíclica | `LoadControl 0.0001919754271453254` x 5209, `test NormDispIncr 0.0001 100 0 2` |
| registrador | `ladruno -N displacement reactionForce -R 2` |
